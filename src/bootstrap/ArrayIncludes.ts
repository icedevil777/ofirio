export default async function() {
  Array.prototype.includesAnyOf = function (...args: any[]) {
    for (let el of arguments)
      if (this.includes(el))
        return true;
    return false;
  } 
}