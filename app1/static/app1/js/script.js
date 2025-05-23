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
// async function cargar_datos() {
//     const SGBD = document.getElementById("SGDB");
//     const fuente = SGBD.value;
//     const ruta = "C:\\Users\\alfredo\\Desktop\\Milton\\Repositorio\\repositorio-django\\DataScience\\ventas_ficticias.csv";
//     const url = "/app1/cargar_datos/";
//     const sep = ";";
//     const usuario_db="cliente";
//     const password_db="cliente1234";
//     const nombre_tabla="ventas_ficticias";
//     const base_datos="data_frames";
    
//     const data = {
//         fuente: fuente,
//         ruta: ruta,
//         usuario_db: usuario_db,
//         password_db:password_db,
//         nombre_tabla: nombre_tabla,
//         base_datos:base_datos,
//         sep:sep,
//     };

//     console.log("Enviando solicitud a:", url, "con data:", data);

//     // mostramos la tabla
//     const tabla_datos = await solicitudPOST(url, data); // ✅ esperar respuesta
//     if (tabla_datos) {  
//         mostrarTabla(tabla_datos);
//         añadir_columnas_section(tabla_datos.columnas,"elegir_columnas");
//         añadir_columnas_section(tabla_datos.columnas,"variable_dependiente");
//     }
// }

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
    const persistente = true;
    const data = {
        filtro: filtro,
        persistente:persistente
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


// codigo para ventana emergente (Conexion a base de datos)
const select_fuente_datos = document.getElementById("SGDB");
const popup = document.getElementById("popup");
const popup2 = document.getElementById("popup2"); //csv 
const popup3 = document.getElementById("popup3"); //excel

const cerrar_popup = document.getElementsByClassName("cerrar");
console.log("evento asociado.. change");

select_fuente_datos.addEventListener("change",function(){
    console.log("ejecutando evento");
    const valor = select_fuente_datos.value;
    if(valor==="csv" ){ 
        popup2.style.display="block"; 
    }
    else if(valor === "excel"){
        popup3.style.display="block";
    }
    else{ 
        popup.style.display = "block"; 
    }
});


for (let i = 0; i < cerrar_popup.length; i++) {
    cerrar_popup[i].addEventListener("click", function () {
    popup.style.display = "none";
    popup2.style.display = "none";
    popup3.style.display="none";
    });
}


// enviar formulario sin recarga
const formulario = document.getElementById("enviar_formulario_csv")
formulario.addEventListener("click",cargar_datos())

async function cargar_datos(){

    
    const url = "/app1/cargar_datos/";
    const archivoInput = document.getElementById("enviar_formulario_csv");
    const archivo = archivoInput.files[0];

    if (!archivo) {
        alert("Por favor, selecciona un archivo.");
        return;
    }

    const data = new FormData();
    data.append("archivo", archivo);
    console.log("Enviando solicitud a:", url, "con data:", data);
    
    const tabla_datos = await solicitudPOST(url, data);
    if (tabla_datos) {  
        mostrarTabla(tabla_datos);
        añadir_columnas_section(tabla_datos.columnas,"elegir_columnas");
        añadir_columnas_section(tabla_datos.columnas,"variable_dependiente");
    }
}