
document.getElementById("entrenarBoton").addEventListener("click", function() {
    fetch("entrenar/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("resultado").innerText = "Error: " + data.error;
        } else {
            document.getElementById("resultado").innerText = 
                `Modelo entrenado con éxito!\nCoeficiente: ${data.coeficiente.toFixed(2)}\nIntercepto: ${data.intercepto.toFixed(2)}`;
        }
    })
    .catch(error => {
        document.getElementById("resultado").innerText = "Error en la petición";
    });
});

// Función para obtener el CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
    
