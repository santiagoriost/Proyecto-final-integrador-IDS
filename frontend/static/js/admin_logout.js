const btnLogout = document.getElementById("btnLogout");
if(btnLogout){
    btnLogout.addEventListener("click", () => {
        localStorage.removeItem("token");
        sessionStorage.clear();
        window.location.href = "/usuario/logout/";

    });

}