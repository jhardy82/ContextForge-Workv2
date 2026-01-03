from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    and_,
    cast,
    literal,
    select,
    union_all,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, aliased, mapped_column, relationship

from .base import Base, BaseRepository


class ContextModel(Base):
    __tablename__ = "contexts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(JSON)  # JSON for cross-db compatibility
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # Dimensions (flattened for legacy compatibility, could be JSONB in future fully)
    dim_motivational: Mapped[str | None] = mapped_column(Text)
    dim_relational: Mapped[str | None] = mapped_column(Text)
    dim_temporal: Mapped[str | None] = mapped_column(Text)
    dim_spatial: Mapped[str | None] = mapped_column(Text)
    dim_resource: Mapped[str | None] = mapped_column(Text)
    dim_operational: Mapped[str | None] = mapped_column(Text)
    dim_risk: Mapped[str | None] = mapped_column(Text)
    dim_policy: Mapped[str | None] = mapped_column(Text)
    dim_knowledge: Mapped[str | None] = mapped_column(Text)
    dim_signal: Mapped[str | None] = mapped_column(Text)
    dim_outcome: Mapped[str | None] = mapped_column(Text)
    dim_emergent: Mapped[str | None] = mapped_column(Text)
    dim_cultural: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class ContextEdgeModel(Base):
    __tablename__ = "context_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contexts.id", ondelete="CASCADE"), index=True
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contexts.id", ondelete="CASCADE"), index=True
    )
    relation_type: Mapped[str] = mapped_column(String, nullable=False)
    attributes: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships? For now we do explicit joins in Repos helper


class ContextRepository(BaseRepository[ContextModel]):
    def __init__(self, session):
        super().__init__(session, ContextModel)

    async def get_by_title_or_id(self, identifier: str) -> ContextModel | None:
        try:
            uuid_val = uuid.UUID(identifier)
            query = select(ContextModel).where(ContextModel.id == uuid_val)
        except ValueError:
            query = select(ContextModel).where(ContextModel.title == identifier)

        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_edge(self, src_id: uuid.UUID, dst_id: uuid.UUID, relation: str) -> bool:
        # Check cycle
        if src_id == dst_id:
            raise ValueError("Self-reference edge not allowed.")

        # Cycle detection CTE
        # WITH RECURSIVE path AS (SELECT dst FROM edges WHERE src=src UNION SELECT e.dst FROM edges e JOIN path p ON e.src=p.dst)
        edges = aliased(ContextEdgeModel)
        path_cte = (
            select(edges.target_id)
            .where(edges.source_id == dst_id)
            .cte(name="path_cte", recursive=True)
        )

        child = aliased(ContextEdgeModel)
        path_cte = path_cte.union_all(
            select(child.target_id).join(path_cte, child.source_id == path_cte.c.target_id)
        )

        # Check if src is reachable from dst
        stmt = select(path_cte).where(path_cte.c.target_id == src_id).limit(1)
        res = await self.session.execute(stmt)
        if res.first():
            raise ValueError(f"Cycle detected: {dst_id} -> ... -> {src_id}")

        edge = ContextEdgeModel(source_id=src_id, target_id=dst_id, relation_type=relation)
        self.session.add(edge)
        return True

    async def get_context_tree(self, root_id: uuid.UUID | None = None) -> list[dict[str, Any]]:
        """
        Equivalent to list_context_tree CTE.
        Returns list of dicts with depth/path info.
        """
        # Aliases
        c = aliased(ContextModel)
        e = aliased(ContextEdgeModel)

        # Base case
        if root_id:
            base_stmt = select(
                c.id,
                c.kind,
                c.title,
                c.summary,
                literal(0).label("depth"),
                cast(literal(str(root_id)), String).label("path"),
            ).where(c.id == root_id)
        else:
            # Roots are those where no incoming 'related_to' edge exists?
            # Or simplified: All nodes
            # Legacy query: NOT EXISTS(select 1 from edges where src=c.id and type='related_to')
            # Wait, legacy logic: src -> dst. If src has no outgoing 'related_to' edge?
            # Let's re-read legacy:
            # WHERE ... NOT EXISTS (SELECT 1 FROM context_edges e WHERE e.src = c.id ... )
            # if edge is src->dst (child->parent logic in legacy seems flipped or src=child? )
            # In legacy `create_context`: `create_edge(result['id'], parent, 'related_to')`
            # So `src` is the child, `dst` is the parent.
            # Root is node with NO PARENT. i.e. NO EDGE where src=this.

            base_stmt = select(
                c.id,
                c.kind,
                c.title,
                c.summary,
                literal(0).label("depth"),
                cast(c.id, String).label("path"),
            ).where(
                ~select(e.id)
                .where(and_(e.source_id == c.id, e.relation_type == "related_to"))
                .exists()
            )
            # Actually easier to just select all if root is None, but let's stick to tree roots logic

        cte = base_stmt.cte(name="context_tree", recursive=True)

        # Recursive part
        # JOIN context_edges e ON e.src = c.id ?
        # Wait, if we are going DOWN the tree (Roots -> Children):
        # Roots are Parents. Children have edges src=Child, dst=Parent.
        # So we want to find C where C points to P (current node in CTE).
        # C -> P. Edge src=C, dst=P.
        # So join e on e.dst = cte.id
        # c on c.id = e.src

        parent_cte = aliased(cte)
        child_c = aliased(ContextModel)
        child_e = aliased(ContextEdgeModel)

        recursive_stmt = (
            select(
                child_c.id,
                child_c.kind,
                child_c.title,
                child_c.summary,
                (parent_cte.c.depth + 1).label("depth"),
                (parent_cte.c.path + "/" + cast(child_c.id, String)).label("path"),
            )
            .join(child_e, child_e.target_id == parent_cte.c.id)
            .join(child_c, child_c.id == child_e.source_id)
            .where(
                child_e.relation_type == "related_to"
                # Cycle check logic often here: AND NOT c.id = ANY(path)
            )
        )

        cte = cte.union_all(recursive_stmt)

        stmt = select(cte)
        res = await self.session.execute(stmt)

        results = []
        for row in res.all():
            d = dict(row._mapping)
            # Parse path string back to list of UUIDs
            if d.get("path"):
                d["path"] = [uuid.UUID(u) for u in d["path"].split("/")]
            else:
                d["path"] = []
            results.append(d)

        return results

    async def resolve_context(self, context_id: uuid.UUID) -> dict[str, Any] | None:
        """
        Merge ancestor attributes.
        """
        # Ancestor Chain CTE: Start at context, go UP to parents (dst).
        # Edge: Child(src) -> Parent(dst)

        c = aliased(ContextModel)
        e = aliased(ContextEdgeModel)

        base_stmt = select(c, literal(0).label("depth")).where(c.id == context_id)

        cte = base_stmt.cte(name="ancestor_chain", recursive=True)

        parent_cte = aliased(cte)  # This is the CHILD in the previous step
        # We want to find the PARENT.
        # Edge: src=child(cte.id), dst=parent(target)

        ancestor_c = aliased(ContextModel)
        ancestor_e = aliased(ContextEdgeModel)

        recursive_stmt = (
            select(ancestor_c, (parent_cte.c.depth + 1).label("depth"))
            .join(
                ancestor_e,
                ancestor_e.source_id == parent_cte.c.id,  # src is child (previous)
            )
            .join(
                ancestor_c,
                ancestor_c.id == ancestor_e.target_id,  # dst is parent (new ancestor)
            )
            .where(ancestor_e.relation_type == "related_to")
        )

        cte = cte.union_all(recursive_stmt)

        # Order by depth DESC (Root first, then children down to target)
        stmt = select(cte).order_by(cte.c.depth.desc())

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # Merge logic (Python side is fine for this volume)
        resolved = {"id": None, "attributes": {}, "ancestors": []}
        target_cols = [
            col for col in ContextModel.__table__.columns.keys() if col.startswith("dim_")
        ]

        # Last row is the target context (depth 0)
        # But we ordered DESC, so first row is Root (highest depth), last row is Target (depth 0).
        # We want to overlay specific over generic.
        # So Root -> ... -> Target.

        target_node = rows[-1]  # This is depth 0 in the list?
        # WAIT: CTE returns rows.
        # ordered by depth desc: 3 (GreatGrand), 2 (Grand), 1 (Parent), 0 (Target).
        # So iterating naturally does: Generic -> Specific. Perfect.

        for row in rows:
            # row is a Row object with the Model columns expanded + depth
            # But since we selected 'c' (the model), it might be nested or flattened depending on alchemy version
            # With `cte` selecting `c`, the columns are available.

            # Extract basic info from the target (last one)
            if row.depth == 0:
                resolved["id"] = row.id
                resolved["title"] = row.title
                resolved["kind"] = row.kind
            else:
                resolved["ancestors"].append({"id": row.id, "title": row.title})

            # Merge dimensions
            for dim in target_cols:
                val = getattr(row, dim, None)
                if val:
                    # Parse JSON if needed
                    if isinstance(val, str):
                        try:
                            parsed = json.loads(val)
                        except:
                            parsed = val
                    else:
                        parsed = val

                    key = dim.replace("dim_", "")
                    if key not in resolved["attributes"]:
                        resolved["attributes"][key] = {}

                    if isinstance(parsed, dict) and isinstance(resolved["attributes"][key], dict):
                        resolved["attributes"][key].update(parsed)
                    else:
                        resolved["attributes"][key] = parsed

        return resolved

    async def list_by_kind(self, kind: str | None = None, limit: int = 20) -> list[ContextModel]:
        stmt = select(ContextModel)
        if kind:
            stmt = stmt.where(ContextModel.kind == kind)
        stmt = stmt.order_by(ContextModel.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_template(self, name: str) -> ContextModel | None:
        stmt = select(ContextModel).where(
            and_(ContextModel.kind == "template", ContextModel.title == name)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
