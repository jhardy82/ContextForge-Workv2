
import {
    Menubar,
    MenubarContent,
    MenubarItem,
    MenubarMenu,
    MenubarRadioGroup,
    MenubarRadioItem,
    MenubarSeparator,
    MenubarShortcut,
    MenubarSub,
    MenubarSubContent,
    MenubarSubTrigger,
    MenubarTrigger
} from "@/components/ui/menubar";

interface AppMenubarProps {
    onCreateTask: () => void;
    onOpenSettings: () => void;
    onToggleView: (view: 'kanban' | 'sprint' | 'analytics' | 'data-explorer') => void;
    currentView: string;
    onTriggerAgent: () => void;
}

export function AppMenubar({
    onCreateTask,
    onOpenSettings,
    onToggleView,
    currentView,
    onTriggerAgent
}: AppMenubarProps) {
  return (
    <Menubar className="rounded-none border-b border-white/5 px-2 lg:px-4 bg-slate-900/40 backdrop-blur-md text-slate-200 supports-[backdrop-filter]:bg-slate-900/20">

      {/* FILE MENU */}
      <MenubarMenu>
        <MenubarTrigger className="font-bold data-[state=open]:bg-slate-800">File</MenubarTrigger>
        <MenubarContent className="bg-slate-900 border-white/10 text-slate-200">
          <MenubarItem onClick={onCreateTask}>
            New Task <MenubarShortcut>C</MenubarShortcut>
          </MenubarItem>
          <MenubarItem disabled>
            New Sprint <MenubarShortcut>⇧S</MenubarShortcut>
          </MenubarItem>
          <MenubarSeparator className="bg-white/10" />
          <MenubarSub>
            <MenubarSubTrigger>Share</MenubarSubTrigger>
            <MenubarSubContent className="bg-slate-900 border-white/10 text-slate-200">
              <MenubarItem>Email link</MenubarItem>
              <MenubarItem>Messages</MenubarItem>
              <MenubarItem>Notes</MenubarItem>
            </MenubarSubContent>
          </MenubarSub>
          <MenubarSeparator className="bg-white/10" />
          <MenubarItem onClick={() => window.print()}>
            Print... <MenubarShortcut>⌘P</MenubarShortcut>
          </MenubarItem>
        </MenubarContent>
      </MenubarMenu>

      {/* EDIT MENU */}
      <MenubarMenu>
        <MenubarTrigger className="data-[state=open]:bg-slate-800">Edit</MenubarTrigger>
        <MenubarContent className="bg-slate-900 border-white/10 text-slate-200">
          <MenubarItem disabled>
            Undo <MenubarShortcut>⌘Z</MenubarShortcut>
          </MenubarItem>
          <MenubarItem disabled>
            Redo <MenubarShortcut>⇧⌘Z</MenubarShortcut>
          </MenubarItem>
          <MenubarSeparator className="bg-white/10" />
          <MenubarItem onClick={onOpenSettings}>
            Preferences...
          </MenubarItem>
        </MenubarContent>
      </MenubarMenu>

      {/* VIEW MENU */}
      <MenubarMenu>
        <MenubarTrigger className="data-[state=open]:bg-slate-800">View</MenubarTrigger>
        <MenubarContent className="bg-slate-900 border-white/10 text-slate-200">
          <MenubarRadioGroup value={currentView}>
            <MenubarRadioItem value="kanban" onClick={() => onToggleView('kanban')}>
                Kanban Board
            </MenubarRadioItem>
            <MenubarRadioItem value="sprint" onClick={() => onToggleView('sprint')}>
                Sprint Planning
            </MenubarRadioItem>
             <MenubarRadioItem value="analytics" onClick={() => onToggleView('analytics')}>
                Analytics & Insights
            </MenubarRadioItem>
             <MenubarRadioItem value="data-explorer" onClick={() => onToggleView('data-explorer')}>
                Data Explorer
            </MenubarRadioItem>
          </MenubarRadioGroup>
          <MenubarSeparator className="bg-white/10" />
          <MenubarItem onClick={onTriggerAgent}>
            Toggle Agent Sidebar <MenubarShortcut>⌘B</MenubarShortcut>
          </MenubarItem>
        </MenubarContent>
      </MenubarMenu>

      {/* TOOLS MENU */}
      <MenubarMenu>
        <MenubarTrigger className="data-[state=open]:bg-slate-800">Tools</MenubarTrigger>
        <MenubarContent className="bg-slate-900 border-white/10 text-slate-200">
            <MenubarItem onSelect={() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }))}>
                Command Palette <MenubarShortcut>⌘K</MenubarShortcut>
            </MenubarItem>
            <MenubarItem onClick={onTriggerAgent}>
                AI Assistant <MenubarShortcut>Ctrl+J</MenubarShortcut>
            </MenubarItem>
        </MenubarContent>
      </MenubarMenu>

    </Menubar>
  )
}
