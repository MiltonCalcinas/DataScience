document.addEventListener("DOMContentLoaded",()=>{
const pagId = document.body.id;
if (pagId ==="login-page"){
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = e.target.username.value;
    const password = e.target.password.value;

    try {
    const res = await fetch('/api/signin/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });

    if (!res.ok) {
        alert('Usuario o contraseña incorrectos');
        return;
    }

    const data = await res.json();

    // Guardar token para futuras peticiones
    localStorage.setItem('token', data.token);

    alert('Inicio de sesión exitoso');
    // Aquí puedes redirigir o actualizar la UI
    // Ejemplo: window.location.href = '/dashboard.html';
    window.location.href ='/';
    await obtenerNombresTablas(); // Llamamos a obtener tablas después de loguear
    } catch (error) {
    console.error('Error al iniciar sesión:', error);
    alert('Error en la conexión');
    }
});


async function obtenerNombresTablas() {
const token = localStorage.getItem('token');

try {
const res = await fetch('/api/table_name/', {
    method: 'GET',
    headers: {
    'Authorization': 'Token ' + token
    }
});

if (!res.ok) throw new Error('No autorizado o error en el servidor');

const data = await res.json();
console.log('Tablas del usuario:', data);
// Puedes renderizar los nombres aquí en la página si quieres
} catch (error) {
console.error('Error al obtener nombres de tablas:', error);
}
}
}


if(pagId=="main-page"){
    
    let df ; 
    let columnasVisibles = new Set();
    const token = localStorage.getItem('token');
    fetch('/api/cargar-tabla-usuario/', {
        method: 'GET',
        headers: {
            'Authorization': 'Token ' + token
        }
    })
    .then(response => response.json())
    .then(data => {
        df = data.tablaCompleta
        console.log(data.preview);
        actualizarTabla(data.preview);
    })
    .catch(error => console.error('Error al cargar la tabla:', error));



// VENTANA EMERGENTE BOTONES
// Obtener elementos
const names_btn = ["btn_generar_grafico","btn_convertir","btn_estadisticas"
]
const names_popup = ["popup_generar_grafico","popup_convertir","popup_estadisticas",
    "popup_transformar_variables"
]
let array_btns =[]
let array_popups = []
let array_cerrar = []
const fin = names_btn.length


for (let i=0 ; i<fin; i++){

    let btn = document.getElementById(names_btn[i]);
    let popup = document.getElementById(names_popup[i]);
    let cerrar = popup.querySelector(".cerrar");



    // Mostrar el popup
    btn.addEventListener("click", () => {
    popup.style.display = "flex";
    });

    // Ocultar el popup al hacer clic en la X
    cerrar.addEventListener("click", () => {
    popup.style.display = "none";
    });

    // Ocultar si se hace clic fuera del contenido (popup)
    window.addEventListener("click", (e) => {
    if (e.target === popup) {
        popup.style.display = "none";
    }
    });

    array_btns.push(btn)
    array_popups.push(popup)
    array_cerrar.push(cerrar)
}




                // VENTANA EMERGENTE CBO

// Obtener elementos
const names_cbo = [ "cbo_transformar_variable","cbo_ANO"
]
const names_popup_cbo = ["popup_transformar_variables","popup_ANO"
]

let array_cbo =[]
let array_popups_cbo = []
let array_cerrar_cbo = []
const end = names_cbo.length


for (let i=0 ; i<end; i++){

    let cbo = document.getElementById(names_cbo[i]);
    let popup_cbo = document.getElementById(names_popup_cbo[i]);
    let cerrar_cbo = popup_cbo.querySelector(".cerrar");



    // Mostrar el popup
    cbo.addEventListener("change", () => {
        // if(cbo.selectedIndex===0){
        //     return;
        // }
        const value = cbo.value;
        const options = ["PCA", "Kmeans", "linkage","ln", "log10", "sqrt", "exp", "square", "abs"];
        if(options.includes(value)){
        popup_cbo.style.display = "flex";
        } else {
        popup_cbo.style.display = "none";
        }

        // cbo.selectedIndex =0;
    });

    // Ocultar el popup al hacer clic en la X
    cerrar_cbo.addEventListener("click", () => {
    popup_cbo.style.display = "none";
    });

    // Ocultar si se hace clic fuera del contenido (popup)
    window.addEventListener("click", (e) => {
    if (e.target === popup_cbo) {
        popup_cbo.style.display = "none";
    }
    });

    array_cbo.push(cbo)
    array_popups_cbo.push(popup_cbo)
    array_cerrar_cbo.push(cerrar_cbo)
}



                        //VENTANA EMERGENTES DE BBDD

document.getElementById('SGDB').addEventListener('change', function() {
    const valor = this.value;

    //Oculta todos los popups primero
    document.querySelectorAll('.popup_sgbd, .popup_csv, .popup_excel').forEach(p => {
        p.style.display = 'flex';  // para que flex funcione en el contenedor
        p.style.justifyContent = 'center';
        p.style.alignItems = 'center';
        p.style.display = 'none';
    });

    // Muestra el popup correspondiente
    if (valor === 'csv') {
        document.getElementById('popup_csv').style.display = 'flex';
    } else if (valor === 'excel') {
        document.getElementById('popup_excel').style.display = 'flex';
    } else if (['MySQL', 'PostgreSQL', 'Microsoft_SQL_Server'].includes(valor)) {
        document.getElementById('popup_sgbd').style.display = 'flex';
    }
});

// Cerrar los popups
document.querySelectorAll('.cerrar').forEach(btn => {
    btn.addEventListener('click', function() {
        this.closest('.popup-contenido').parentElement.style.display = 'none';
    });
});






















//          BACK-END






function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');       //TOKEN
}


document.getElementById("form_excel").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    fetch("/api/subir_excel/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error del servidor");
        }
        return response.json();
    })
    .then(data => {
        if (data.preview && data.preview.length > 0) {
            df = new dfd.DataFrame(data.tablaCompleta);   // Guardamos todo el contenido
            console.log(df.head(1));
            console.log(data.preview[0]);
            actualizarTabla(data.preview);      // Mostrar 50 filas
        }
        alert("Archivo subido correctamente.");
        document.getElementById("popup_excel").style.display = "none";
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Hubo un error al enviar el formulario.");
    });
});

document.getElementById("formulario_csv").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    fetch("/api/subir_csv/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error del servidor");
        }
        return response.json();
    })
    .then(data => {
        if (data.preview && data.preview.length > 0) {
            df = new dfd.DataFrame(data.tablaCompleta); 
            console.log(df.head(1));
            console.log(data.preview[0]);
            actualizarTabla(data.preview);
        }
        alert("Archivo subido correctamente.");
        document.getElementById("popup_csv").style.display = "none";
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Hubo un error al enviar el formulario.");
    });
});



document.getElementById("formulario_sgbd").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    const tipo_sgbd = document.getElementById("SGDB").value;
    formData.append("tipo_sgbd", tipo_sgbd);

    fetch("/api/conectarser_sgbd_cliente/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error("Error del servidor");
        return response.json();
    })
    .then(data => {
        if (data.preview && data.preview.length > 0) {
            df = new dfd.DataFrame(data.tablaCompleta); 
            console.log(df.head(1));
            console.log(data.preview[0]);
            actualizarTabla(data.preview);
        }
        alert(data.mensaje || "Conexión exitosa");
        document.getElementById("popup_sgbd").style.display = "none";
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Hubo un error al enviar el formulario.");
    });
});




function actualizarTabla(filas) {
    const contenedor = document.getElementById("tabla_datos");

    // Limpiar tabla previa
    contenedor.innerHTML = "";

    const tabla = document.createElement("table");

    // Crear encabezado
    const encabezados = Object.keys(filas[0]);
    const thead = document.createElement("thead");
    const trHead = document.createElement("tr");
    encabezados.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col;
        trHead.appendChild(th);
    });
    thead.appendChild(trHead);
    tabla.appendChild(thead);

    // Crear cuerpo de la tabla
    const tbody = document.createElement("tbody");
    filas.forEach(fila => {
        const tr = document.createElement("tr");
        encabezados.forEach(col => {
            const td = document.createElement("td");
            td.textContent = fila[col];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);

    // Insertar la nueva tabla en el contenedor
    contenedor.appendChild(tabla);
}



const btn_columnas = document.getElementById("btn_columnas");
const popup_columnas = document.getElementById("popup_columnas");
const cerrar_columnas = popup_columnas.querySelector(".cerrar");
const btn_eliminar = document.getElementById("btn_eliminar_columnas");

btn_columnas.addEventListener("click", () => {
    //if (!tablaCompleta.length) return;

    popup_columnas.style.display = "flex";

    const columnas = df.columns;
    const form = document.getElementById("form_columnas");
    form.innerHTML = "";  // Limpiar

    columnas.forEach(col => {
        const label = document.createElement("label");
        label.innerHTML = `<input type="checkbox" value="${col}" checked> ${col}`;
        form.appendChild(label);
        form.appendChild(document.createElement("br"));
    });


});

// Listener para eliminar columnas
btn_eliminar.addEventListener("click", () => {
    const form = document.getElementById("form_columnas");
    const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
    const columnasSeleccionadas = Array.from(checkboxes).map(cb => cb.value);
    console.log(columnasSeleccionadas)

    // Crear nuevo DataFrame con solo las columnas seleccionadas
    df = df.loc({columns: columnasSeleccionadas});
    console.log(df.head(1))
    const arrayDeObjetos = dfd.toJSON(df.head(50), { format: 'column' })
    console.log(arrayDeObjetos);
    actualizarTabla(arrayDeObjetos);
    
    // Cerrar popup
    popup_columnas.style.display = "none";
});





// Ocultar el popup al hacer clic en la X
cerrar_columnas.addEventListener("click", () => {
popup_columnas.style.display = "none";
});

// Ocultar si se hace clic fuera del contenido (popup_columnas)
window.addEventListener("click", (e) => {
if (e.target === popup_columnas) {
    popup_columnas.style.display = "none";
}
});


const btn_aplicar = document.getElementById("btn_aplicar");
btn_aplicar.addEventListener("click",()=>{
    // enviar al back-end para que guarde en bbdd
});





const btn_filtar = document.getElementById("btn_filtrar");
let popup_filtrar = document.getElementById("popup_filtrar");
let cerrar_filtar = popup_filtrar.querySelector(".cerrar");



// Mostrar el popup
btn_filtar.addEventListener("click", () => {
    if(df===undefined){
        console.log("No has cargado Tabla")
        return;}


    popup_filtrar.style.display = "flex";

    const form = document.getElementById("form_filtrar");
    const tipos = obtenerTipos(df);
    console.log(tipos);
    console.log(df.head(1))
    const columnas = df.columns;
    console.log(columnas)
    const operadores = {
        number: [">", "<", ">=", "<=", "==", "!="],
        string: ["==", "!=", "includes"]
    };

    for (let i = 0; i < 3; i++) {
        const fila = document.createElement("div");
        fila.style.marginBottom = "8px";

        // 1. Select de columnas
        const cboColumna = document.createElement("select");
        columnas.forEach(col => {
            const option = document.createElement("option");
            option.value = col;
            option.textContent = col;
            cboColumna.appendChild(option);
        });
        console.log("Corecto cboColumna")
        // 2. Select de operadores (por defecto según la primera columna)
        const cboOperador = document.createElement("select");
        const tipoInicial = tipos[columnas[0]];
        console.log(tipoInicial)
        operadores[tipoInicial].forEach(op => {
            const option = document.createElement("option");
            option.value = op;
            option.textContent = op;
            cboOperador.appendChild(option);
        });
        console.log("Operador no falla")

        // Cambiar operadores si cambia la columna seleccionada
        cboColumna.addEventListener("change", () => {
            const tipo = tipos[cboColumna.value];
            cboOperador.innerHTML = "";
            operadores[tipo].forEach(op => {
                const option = document.createElement("option");
                option.value = op;
                option.textContent = op;
                cboOperador.appendChild(option);
            });
        });
        console.log("Operador no falla")

        // 3. Input de valor
        const inputValor = document.createElement("input");
        inputValor.type = "text";

        fila.appendChild(cboColumna);
        fila.appendChild(cboOperador);
        fila.appendChild(inputValor);

        form.appendChild(fila);
        }
});

function obtenerTipos(df) {
    const tipos = {};
    df.columns.forEach(col => {
        const serie = df.column(col);
        const primerValor = serie.values[0];

        // Comprobar si el tipo es number o string
        if (typeof primerValor === "number") {
            tipos[col] = "number";
        } else {
            tipos[col] = "string";
        }
    });
    return tipos;
}

// Ocultar el popup al hacer clic en la X
cerrar_filtar.addEventListener("click", () => {
popup_filtrar.style.display = "none";
});

// Ocultar si se hace clic fuera del contenido (popup)
window.addEventListener("click", (e) => {
if (e.target === popup_filtrar) {
    popup_filtrar.style.display = "none";
}   
});


        
    }
});
