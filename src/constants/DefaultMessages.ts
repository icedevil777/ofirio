import env from '@/models/env.model';

export const APP_DEFAULT_SMTH_BAD_FROM_SERVER = {
  type: env.VUE_APP_DEFAULT_SERVER_ERROR_TYPE,
  message: env.VUE_APP_DEFAULT_SERVER_ERROR_TEXT
}

export const APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED = <TServerDefaultResponse>{
  server_messages: [
    {
      level: env.VUE_APP_DEFAULT_SERVER_ERROR_TYPE,
      message: env.VUE_APP_DEFAULT_SERVER_ERROR_TEXT
    }
  ]
}