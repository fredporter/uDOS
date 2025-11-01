
export function ttParse(input){
  const map = {
    '{RED}': '<span class="tt-fg-red">', '{GRN}': '<span class="tt-fg-grn">', '{YEL}': '<span class="tt-fg-yel">',
    '{BLU}': '<span class="tt-fg-blu">', '{MAG}': '<span class="tt-fg-mag">', '{CYN}': '<span class="tt-fg-cyn">', '{WHT}': '<span class="tt-fg-wht">',
    '{SEP}': '<span class="tt-sep">', '{CON}': '<span class="tt-con">', '{DBLH}': '<div class="tt-dblh">', '{/DBLH}': '</div>',
    '{FLASH}': '<span class="tt-flash">'
  };
  let out = input.replace(/\{\/(RED|GRN|YEL|BLU|MAG|CYN|WHT|SEP|CON|FLASH)\}/g, '</span>');
  Object.entries(map).forEach(([k,v])=>{ out = out.split(k).join(v); });
  return out;
}
