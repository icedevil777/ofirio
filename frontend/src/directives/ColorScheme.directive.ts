import { colorSchemePipeStyle } from '@/pipes/ColorSchemes.pipe';

function VueDirectiveSetColor(el: HTMLElement, binding: any) {
  let color = colorSchemePipeStyle(binding.arg, binding.value);
  el.style.color = color.color || '';
}

export const ColorSchemeDirective = {
  mounted: VueDirectiveSetColor,
  updated: VueDirectiveSetColor
};

export default ColorSchemeDirective;