import envModel from '@/models/env.model';

export type TOfirioEvent = {
  time: number,
  name: string,
  data?: any
}


const localStorage_key_name = 'ofirio-glob-events';
const loadState = function (data?: string) {
  return <Array<TOfirioEvent>>JSON.parse( data ? data : window.localStorage.getItem(localStorage_key_name) || '[]');
}
const setState = function (events: Array<TOfirioEvent>) {
  window.localStorage.setItem(localStorage_key_name, JSON.stringify(events));
}


let lastNotificationTime = 0;
export const sendEvent = function (name: string, data?: any) {

  let state = loadState();
  const time = Date.now();
  lastNotificationTime = time;
  
  state.unshift({ name, data, time });
  if (state.length > envModel.VUE_APP_LOCALSTORAGE_EVENTS_BUFFER)
    state.pop();

  setState(state);
}

const getEvent = function (e: StorageEvent) {
  if (e.key != localStorage_key_name || !e.newValue)
    return;

  const state = loadState(e.newValue);

  if (state.length < 1)
    return;

  for (let ev of state) {
    if (ev.time == lastNotificationTime)
      break;
    notify(ev);
  }

  lastNotificationTime = state[0].time;
}



const watchers:Record<string, Array<Function>> = {};
const notify = function (ev: TOfirioEvent) {
  if (watchers[ev.name] == undefined)
    return;
  watchers[ev.name].forEach(cb => cb(ev.data));
}
export const observe = function (eventName: string, callback: Function) {
  if (watchers[eventName] == undefined)
    watchers[eventName] = [];
  
  watchers[eventName].push(callback);

  return function () {
    if (watchers[eventName] == undefined)
      return;
    const i = watchers[eventName].indexOf(callback);
    watchers[eventName].splice(i, 1);
  }
}




const initState = loadState();
if (initState.length > 0)
  lastNotificationTime = initState[0].time;

window.addEventListener('storage', getEvent);