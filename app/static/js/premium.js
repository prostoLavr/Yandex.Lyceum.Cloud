const num = document.getElementById('num');
const rng = document.getElementById('range');
const view = document.getElementById('view');
const set = val => {
  num.value = val;
  rng.value = val;
  view.textContent = val + ' ГБ';
}

rng.addEventListener('input', () => set(rng.value));
num.addEventListener('change', () => set(num.value));