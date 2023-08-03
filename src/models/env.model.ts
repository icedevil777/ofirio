type VUE_ENV = {
  VUE_APP_DEVMODE: boolean,
  VUE_APP_API_URL_PREFIX: string,
  VUE_APP_API_GOOGLE_MAP_TOKEN: string,
  VUE_APP_CSRF_TOKEN: string,
  VUE_APP_MOBILE_WIDTH: string,
  VUE_APP_LOCALSTORAGE_EVENTS_BUFFER: number,
  VUE_APP_DEFAULT_SERVER_ERROR_TYPE: 'error' | 'warning' | 'success' | 'info',
  VUE_APP_DEFAULT_SERVER_ERROR_TEXT: string
  VUE_APP_TERMS_UPDATE_DATE: string
}
type customParams = {
  mode: string,
  __initEnd?: Promise<void>
}

let envModel = <VUE_ENV & customParams><unknown>process.env;
envModel.mode = <string>process.env.NODE_ENV;
export default envModel;