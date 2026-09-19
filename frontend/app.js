const API = "";

let busquedaTimer = null;

function headers() {
  const token = sessionStorage.getItem("token");
  const resultado = { "Content-Type": "application/json" };
  if (token) {
    resultado.Authorization = `Bearer ${token}`;
  }
  return resultado;
}

function mostrarError(id, mensaje) {
  const caja = document.getElementById(id);
  caja.textContent = mensaje;
  caja.classList.toggle("hidden", !mensaje);
}

function mostrarApp(usuario) {
  document.getElementById("vista-login").classList.add("hidden");
  document.getElementById("vista-app").classList.remove("hidden");
  document.getElementById("nombre-usuario").textContent = usuario;
  cargarLista();
}

function mostrarLogin() {
  sessionStorage.clear();
  document.getElementById("vista-app").classList.add("hidden");
  document.getElementById("vista-login").classList.remove("hidden");
}

function dinero(valor) {
  return `Q ${Number(valor).toFixed(2)}`;
}

function pintarResultado(datos) {
  document.getElementById("resultado").classList.remove("hidden");
  document.getElementById("res-id").textContent = datos.id;
  document.getElementById("res-sac").textContent = `SAC ${datos.categoria}`;
  document.getElementById("res-desc").textContent = datos.descripcion || "";
  document.getElementById("res-tasa").textContent = `${(Number(datos.tasa_dai) * 100).toFixed(0)}%`;
  document.getElementById("res-cif").textContent = dinero(datos.cif);
  document.getElementById("res-dai").textContent = dinero(datos.dai);
  document.getElementById("res-iva").textContent = dinero(datos.iva);
  document.getElementById("res-impuestos").textContent = dinero(datos.total_impuestos);
  document.getElementById("res-total").textContent = dinero(datos.total);
}

function elegirArancel(item) {
  document.getElementById("categoria").value = item.codigo;
  document.getElementById("buscar-arancel").value = item.codigo;
  document.getElementById("arancel-elegido").textContent =
    `${item.codigo} · DAI ${item.dai_nmf}% · ${item.descripcion}`;
  document.getElementById("sugerencias-arancel").innerHTML = "";
}

function pintarSugerencias(items) {
  const caja = document.getElementById("sugerencias-arancel");
  if (!items.length) {
    caja.innerHTML = '<p class="text-xs text-slate-400">Sin coincidencias en el arancel 2026.</p>';
    return;
  }

  caja.innerHTML = items
    .map(
      (item) => `
      <button
        type="button"
        class="block w-full rounded-lg border border-slate-200 px-3 py-2 text-left text-sm hover:border-aduana-400 hover:bg-aduana-100"
        data-codigo="${item.codigo}"
      >
        <span class="font-semibold text-aduana-900">${item.codigo}</span>
        <span class="text-aduana-600"> · ${item.dai_nmf}%</span>
        <span class="mt-0.5 block text-xs text-slate-500">${item.descripcion}</span>
      </button>
    `
    )
    .join("");

  caja.querySelectorAll("button[data-codigo]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const item = items.find((x) => x.codigo === boton.dataset.codigo);
      if (item) elegirArancel(item);
    });
  });
}

function pintarLista(cotizaciones) {
  const contenedor = document.getElementById("lista-cotizaciones");
  if (!cotizaciones.length) {
    contenedor.innerHTML =
      '<p class="text-sm text-slate-400">Aún no tienes cotizaciones. Calcula la primera a la izquierda.</p>';
    return;
  }

  contenedor.innerHTML = cotizaciones
    .map(
      (item) => `
      <button
        type="button"
        data-id="${item.id}"
        class="flex w-full items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-left hover:border-aduana-400 hover:bg-aduana-100"
      >
        <span>
          <span class="block font-semibold text-aduana-900">${item.categoria}</span>
          <span class="block text-xs text-slate-500">${item.descripcion || "Sin descripción"}</span>
        </span>
        <span class="font-semibold text-aduana-800">${dinero(item.total)}</span>
      </button>
    `
    )
    .join("");

  contenedor.querySelectorAll("button[data-id]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const seleccionada = cotizaciones.find((item) => item.id === boton.dataset.id);
      if (seleccionada) {
        pintarResultado(seleccionada);
      }
    });
  });
}

async function pedir(ruta, opciones) {
  const respuesta = await fetch(`${API}${ruta}`, opciones);
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    throw new Error(datos.error || "No se pudo completar la operación");
  }
  return datos;
}

async function cargarLista() {
  mostrarError("error-lista", "");
  try {
    const cotizaciones = await pedir("/cotizaciones", { headers: headers() });
    pintarLista(cotizaciones);
  } catch (error) {
    if (error.message === "No autenticado") {
      mostrarLogin();
      return;
    }
    mostrarError("error-lista", error.message);
  }
}

document.getElementById("buscar-arancel").addEventListener("input", (evento) => {
  const q = evento.target.value.trim();
  document.getElementById("categoria").value = "";
  document.getElementById("arancel-elegido").textContent = "";
  clearTimeout(busquedaTimer);
  if (q.length < 2) {
    document.getElementById("sugerencias-arancel").innerHTML = "";
    return;
  }
  busquedaTimer = setTimeout(async () => {
    try {
      const items = await pedir(`/aranceles?q=${encodeURIComponent(q)}`, { headers: headers() });
      pintarSugerencias(items);
    } catch (error) {
      document.getElementById("sugerencias-arancel").innerHTML =
        `<p class="text-xs text-red-600">${error.message}</p>`;
    }
  }, 250);
});

document.getElementById("form-login").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarError("error-login", "");
  try {
    const datos = await pedir("/login", {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        usuario: document.getElementById("usuario").value,
        clave: document.getElementById("clave").value,
      }),
    });
    sessionStorage.setItem("token", datos.token);
    sessionStorage.setItem("usuario", datos.usuario);
    mostrarApp(datos.usuario);
  } catch (error) {
    mostrarError("error-login", error.message);
  }
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  try {
    await pedir("/logout", { method: "POST", headers: headers() });
  } finally {
    mostrarLogin();
  }
});

document.getElementById("form-cotizar").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarError("error-cotizar", "");
  const codigo = document.getElementById("categoria").value;
  if (!codigo) {
    mostrarError("error-cotizar", "Busca y elige un código SAC del arancel");
    return;
  }
  try {
    const datos = await pedir("/cotizaciones", {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        fob: document.getElementById("fob").value,
        flete: document.getElementById("flete").value,
        seguro: document.getElementById("seguro").value,
        categoria: codigo,
      }),
    });
    pintarResultado(datos);
    await cargarLista();
  } catch (error) {
    mostrarError("error-cotizar", error.message);
  }
});

if (sessionStorage.getItem("token")) {
  mostrarApp(sessionStorage.getItem("usuario") || "admin");
}
