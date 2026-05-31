flatpickr("input[type='date']", {
    dateFormat: "d/m/Y",
    minDate: "today",
    disableMobile: true
});

flatpickr("input[type='time']", {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: false,
    disableMobile: true
});
document.addEventListener("wheel", function(event){
    const reloj = event.target.closest(".flatpickr-time");

    if(reloj){
        event.preventDefault();
    }
}, { passive: false });