# ofirio-fe



## Code
```
Prefixes:
I - Interface
T- Type
V - Validator
UI - UI component
P - Page
```

## Project setup
```
npm install
```
  If you experiencing some problems with npm (found on npm 7.20) like:
```
  ETARGET
  notarget No matching version found for @vue/cli-ui-addon-webpack@^4.5.13
```
  then downgrade to npm v7.19
  

### Compiles and hot-reloads for development
```

export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm use 12

npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
