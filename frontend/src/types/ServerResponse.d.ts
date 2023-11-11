// Axios Typings
type AxiosRequestToAwaiting<R> = Promise<[import('axios').AxiosResponse<R>, import('axios').AxiosError?]>

// Default Server Response types
type TServerDefaultMessageType = 'debug' | 'info' | 'success' | 'warning' | 'error';
type TServerDefaultMessageObject = {
  level: TServerDefaultMessageType,
  message: string
};

type TServerDefaultResponse = {
  server_messages: TServerDefaultMessageObject[]
}