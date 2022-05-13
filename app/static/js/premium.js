const num = document.getElementById('num');
const rng = document.getElementById('range');
const view = document.getElementById('view');
const goods = document.querySelectorAll('.good');
const set = val => {
  num.value = val;
  rng.value = val;
  view.textContent = val;
  [...goods].forEach(good => {
    const options = good.querySelectorAll('.option');
    [...options].forEach(option => {
      option.style.display = val >= +option.dataset.from ? 'block': 'none';
    });
  });
}

rng.addEventListener('input', () => set(rng.value));
num.addEventListener('change', () => set(num.value));