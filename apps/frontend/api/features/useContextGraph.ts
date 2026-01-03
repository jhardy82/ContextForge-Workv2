
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

// Align with Backend `ContextResponse` or the specific CTE result
export interface ContextNodeData {
  id: string;
  kind: string;
  title: string;
  summary?: string;
  depth: number;
  path: string[]; // List of UUIDs
}

const getApiUrl = () => localStorage.getItem('taskman_api_url') || 'http://localhost:3001/api/v1';

export const useContextGraph = () => {
    return useQuery({
        queryKey: ['/api/v1/context/tree'],
        queryFn: async (): Promise<ContextNodeData[]> => {
            const { data } = await axios.get(`${getApiUrl()}/context/tree`);
            return data;
        },
        staleTime: 60 * 1000, // 1 minute
    });
};
