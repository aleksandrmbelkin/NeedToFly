const input = document.getElementById('search_from');
const datalist = document.getElementById('items_from');
const allItems = ["Яблоко", "Апельсин", "Банан", "Груша", "Виноград", "Ананас", "Киви"];

input.addEventListener('input', () => {
    const query = input.value.toLowerCase();
    const filteredItems = allItems
    .filter(item => item.toLowerCase().includes(query))
    .slice(0, 3);

    datalist.innerHTML = '';
    filteredItems.forEach(item => {
        const option = document.createElement('option');
        option.value = item;
        datalist.appendChild(option);
    });
});