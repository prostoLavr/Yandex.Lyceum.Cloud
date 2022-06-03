function copyText(link) {
    const el = document.createElement("textarea");
    el.value = link;
    el.setAttribute("readonly", "");
    el.style.position = "absolute";
    el.style.left = "-9999px";
    document.body.appendChild(el);
    el.select();
    el.setSelectionRange(0, 99999);
    document.execCommand("copy");
    document.body.removeChild(el);
    document.getElementById("linkButton").textContent = "Ссылка скопирована!"
}