import axios, { AxiosRequestConfig } from 'axios';

// Create a configured axios instance
// Base URL is empty to allow Vite proxy to handle '/api' requests to backend
export const AXIOS_INSTANCE = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors can be added here
AXIOS_INSTANCE.interceptors.response.use(
  (response) => response,
  (error) => {
    // Standardized error handling could go here
    return Promise.reject(error);
  }
);

// Custom fetcher function compatible with Orval
export const customInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const source = axios.CancelToken.source();
  const promise = AXIOS_INSTANCE({
    ...config,
    ...options,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-ignore
  promise.cancel = () => {
    source.cancel('Query was cancelled');
  };

  return promise;
};
