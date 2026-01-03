import {
    useAddItemToActionListApiV1ActionListsListIdItemsPost,
    useCreateActionListApiV1ActionListsPost,
    useDeleteActionListApiV1ActionListsListIdDelete,
    useListActionListsApiV1ActionListsGet,
    useUpdateActionListApiV1ActionListsListIdPut
} from '@/api/generated/action-lists/action-lists';
import { useQueryClient } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle, Circle, Plus, Trash2 } from 'lucide-react';
import React, { useState } from 'react';
import { toast } from 'sonner';
import { ActionList } from '../../lib/types';

export const ActionListView: React.FC = () => {
    const queryClient = useQueryClient();
    const [newListTitle, setNewListTitle] = useState('');
    const [newItemText, setNewItemText] = useState<Record<string, string>>({});

    // Query: Fetch all action lists
    const { data: actionListCollection, isLoading: loading, refetch } = useListActionListsApiV1ActionListsGet();

    // Map to legacy ActionList type for compatibility
    const lists: ActionList[] = (actionListCollection?.action_lists || []).map((list: any) => ({
        ...list,
        items: list.items || []
    }));

    // Mutations
    const createListMutation = useCreateActionListApiV1ActionListsPost();
    const deleteListMutation = useDeleteActionListApiV1ActionListsListIdDelete();
    const addItemMutation = useAddItemToActionListApiV1ActionListsListIdItemsPost();
    const updateListMutation = useUpdateActionListApiV1ActionListsListIdPut();

    const handleCreateList = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newListTitle.trim()) return;

        try {
            await createListMutation.mutateAsync({
                data: {
                    title: newListTitle,
                    status: 'active',
                    priority: 'medium',
                    // items: [] - items are managed separately via item endpoints
                } as any
            });
            setNewListTitle('');
            toast.success("Action list created");
            refetch();
        } catch (error) {
            toast.error("Failed to create action list");
        }
    };

    const handleDeleteList = async (id: string) => {
        try {
            await deleteListMutation.mutateAsync({ listId: id });
            toast.success("List deleted");
            refetch();
        } catch (error) {
            toast.error("Failed to delete list");
        }
    };

    const handleAddItem = async (listId: string) => {
        const text = newItemText[listId];
        if (!text?.trim()) return;

        try {
            await addItemMutation.mutateAsync({
                listId: listId,
                data: { text }
            });
            setNewItemText({ ...newItemText, [listId]: '' });
            refetch();
        } catch (error) {
            toast.error("Failed to add item");
        }
    };

    const handleToggleItem = async (listId: string, itemId: string) => {
        // Find the current list and item
        const list = lists.find(l => l.id === listId);
        if (!list) return;

        const item = list.items.find(i => i.id === itemId);
        if (!item) return;

        // Toggle is_completed via update endpoint
        // We update the entire items array with the toggled item
        const updatedItems = list.items.map(i =>
            i.id === itemId ? { ...i, is_completed: !i.is_completed } : i
        );

        try {
            await updateListMutation.mutateAsync({
                listId,
                data: {
                    items: updatedItems as any
                }
            });
            refetch();
        } catch (error) {
            toast.error("Failed to toggle item");
            // Revert on error
            refetch();
        }
    };

    return (
        <div className="space-y-6 p-6">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <span className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/50">
                            📝
                        </span>
                        Action Lists
                        <span className="text-sm font-normal text-slate-400 ml-4 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700">
                            React Query
                        </span>
                    </h2>
                    <p className="text-slate-400 mt-2 max-w-2xl">
                        Fast-paced checklists for immediate execution. Synced directly with the backend.
                    </p>
                </div>
            </header>

            {/* Create New List */}
            <form onSubmit={handleCreateList} className="glass p-4 rounded-xl flex gap-4 items-center border border-white/5">
                <input
                    type="text"
                    value={newListTitle}
                    onChange={(e) => setNewListTitle(e.target.value)}
                    placeholder="Create a new action list..."
                    className="bg-transparent flex-1 outline-none text-white placeholder:text-slate-500"
                />
                <button
                    type="submit"
                    disabled={!newListTitle.trim()}
                    className="bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                    <Plus size={20} />
                </button>
            </form>

            {/* Grid of Lists */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence>
                    {lists.map(list => (
                        <motion.div
                            key={list.id}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="glass-card p-5 rounded-xl border border-white/5 hover:border-emerald-500/30 transition-colors group"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-xl font-semibold text-white truncate pr-4">{list.title}</h3>
                                <button
                                    onClick={() => handleDeleteList(list.id)}
                                    className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>

                            {/* Items */}
                            <ul className="space-y-2 mb-4 min-h-[100px]">
                                {list.items.length === 0 && (
                                    <p className="text-slate-600 italic text-sm text-center py-4">No items yet</p>
                                )}
                                {list.items.map(item => (
                                    <li key={item.id} className="flex items-start gap-3 group/item">
                                        <button
                                            onClick={() => handleToggleItem(list.id, item.id)}
                                            className={`mt-1 transition-colors ${item.is_completed ? 'text-emerald-400' : 'text-slate-500 hover:text-emerald-400'}`}
                                        >
                                            {item.is_completed ? <CheckCircle size={18} /> : <Circle size={18} />}
                                        </button>
                                        <span className={`text-sm flex-1 break-words ${item.is_completed ? 'text-slate-500 line-through' : 'text-slate-200'}`}>
                                            {item.text}
                                        </span>
                                    </li>
                                ))}
                            </ul>

                            {/* Add Item Input */}
                            <div className="flex gap-2 items-center mt-auto pt-4 border-t border-white/5">
                                <input
                                    type="text"
                                    placeholder="Add item..."
                                    value={newItemText[list.id] || ''}
                                    onChange={(e) => setNewItemText({ ...newItemText, [list.id]: e.target.value })}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAddItem(list.id)}
                                    className="bg-transparent flex-1 text-sm outline-none text-white placeholder:text-slate-600"
                                />
                                <button
                                    onClick={() => handleAddItem(list.id)}
                                    className="text-slate-500 hover:text-emerald-400"
                                >
                                    <Plus size={16} />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {loading && (
                <div className="flex justify-center items-center py-20">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
                </div>
            )}
        </div>
    );
};
