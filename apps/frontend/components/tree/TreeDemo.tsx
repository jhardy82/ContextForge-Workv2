import { Card } from '@/components/ui/card';
import { generateTaskTree } from '@/mocks/data-generator';
import { useMemo } from 'react';
import { TreeView } from './TreeView';

export function TreeDemo() {
  // Generate 1000 items hierarchically
  const data = useMemo(() => {
    const start = performance.now();
    const roots = generateTaskTree(50); // 50 roots

    // Add children recursively to valid depth
    roots.forEach(root => {
        root.children = generateTaskTree(5); // 5 children each
        root.children.forEach(child => {
            child.children = generateTaskTree(3); // 3 grand children
        });
    });

    // Total approx: 50 + (50*5) + (250*3) = 50 + 250 + 750 = 1050 nodes
    console.log(`[TREE DEMO] Generated ~1000 nodes in ${performance.now() - start}ms`);
    return roots;
  }, []);

  return (
    <div className="p-8 h-screen bg-slate-950 flex flex-col">
      <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-600 mb-4">
        Tree View Component Demo
      </h1>
      <Card className="flex-1 border-white/10 bg-black/20 backdrop-blur overflow-hidden">
        <TreeView
            data={data}
            onSelectNode={(node) => console.log('Selected:', node.title)}
            className="p-2"
        />
      </Card>
    </div>
  );
}
