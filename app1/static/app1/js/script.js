// ✅ Ahora es una función async que espera la respuesta de fetch
async function solicitudPOST(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', 
            },
            body: JSON.stringify(data)
        });

        const jsonData = await response.json();
        console.log("Respuesta Recibida:", jsonData);
        return jsonData;

    } catch (error) {
        console.error("Error en la solicitud:", error);
        return null;
    }
}


// ✅
function mostrarTabla(tabla_datos) {
    const columnas = tabla_datos.columnas;
    const filas = tabla_datos.filas;
    const contenedor = document.getElementById("tabla_datos"); // div

    // Limpiar contenido anterior
    contenedor.innerHTML = "";

    // Crear la tabla
    const tabla = document.createElement("table");
    contenedor.appendChild(tabla);

    // Cabecera
    const filaCabecera = tabla.insertRow();
    columnas.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col.charAt(0).toUpperCase() + col.slice(1).toLowerCase();
        filaCabecera.appendChild(th);
    });

    // Filas de datos
    filas.forEach(fila => {
        const tr = tabla.insertRow();
        columnas.forEach(col => {
            const td = tr.insertCell();
            td.textContent = fila[col];
        });
    });
}


// ✅ Cargamos vistazo de la Tabla y Nombres de columnas en ComboBox que lo quiera
async function cargar_datos() {
    const SGBD = document.getElementById("SGDB");
    const fuente = SGBD.value;
    const ruta = "C:\\Users\\alfredo\\Desktop\\Milton\\Repositorio\\repositorio-django\\DataScience\\ventas_ficticias.csv";
    const url = "/app1/cargar_datos/";
    const sep = ";";

    const data = {
        fuente: fuente,
        ruta: ruta,
        sep: sep,
    };

    console.log("Enviando solicitud a:", url, "con data:", data);

    // mostramos la tabla
    const tabla_datos = await solicitudPOST(url, data); // ✅ esperar respuesta
    if (tabla_datos) {  
        mostrarTabla(tabla_datos);
        añadir_columnas_section(tabla_datos.columnas,"elegir_columnas");
        añadir_columnas_section(tabla_datos.columnas,"variable_dependiente");
    }
}

function añadir_columnas_section(columnas,id){
    section = document.getElementById(id);
    section.innerHTML="";
    columnas.forEach(col=>{
        const option = document.createElement("option");
        option.textContent = col;
        option.value=col;
        section.appendChild(option);
    }

    )
}

async function filtrar_datos(event){
    if(event.key!="Enter"){
        return null;
    }

    const filtro = inputFiltrar.value;
    const data = {
        filtro: filtro,
    };
    const url = "/app1/filtrar/";

    const tabla_datos_filtrado = await solicitudPOST(url,data);
    console.log("solicitud de filtro enviada",filtro);

    if(tabla_datos_filtrado){ 
        mostrarTabla(tabla_datos_filtrado)
    }

}



const aplicar = document.getElementById("btn_aplicar");
aplicar.addEventListener("click", cargar_datos);

const inputFiltrar = document.getElementById("search");
inputFiltrar.addEventListener("keydown",filtrar_datos)
