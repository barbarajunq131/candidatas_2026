"use strict";

const estado = {
  pagina: "negras",
  dados: [],
  filtros: { cargo: "", partido: "", pauta: "", raca: "", busca: "" },
};

const $ = (seletor) => document.querySelector(seletor);
const $$ = (seletor) => [...document.querySelectorAll(seletor)];

function escapar(valor = "") {
  return String(valor).replace(/[&<>'"]/g, (caractere) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[caractere]);
}

function semAcento(valor = "") {
  return String(valor).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();
}

function preencherSelect(id, valores, primeiro) {
  const select = $(id);
  select.innerHTML = `<option value="">${primeiro}</option>` + valores
    .map((valor) => `<option value="${escapar(valor)}">${escapar(valor)}</option>`)
    .join("");
}

function opcoesDaPagina(campo) {
  return [...new Set(baseDaPagina().flatMap((item) => campo === "pautas" ? item.pautas : [item[campo]]).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, "pt-BR"));
}

function baseDaPagina() {
  if (estado.pagina === "negras") {
    return estado.dados.filter((item) => ["PRETA", "PARDA"].includes(item.cor_raca_tse));
  }
  return estado.dados;
}

function aplicarFiltros() {
  const f = estado.filtros;
  return baseDaPagina().filter((item) => {
    if (f.cargo && item.cargo !== f.cargo) return false;
    if (f.partido && item.partido !== f.partido) return false;
    if (f.pauta && !item.pautas.includes(f.pauta)) return false;
    if (f.raca && item.cor_raca_tse !== f.raca) return false;
    if (f.busca) {
      const busca = semAcento(f.busca);
      const texto = semAcento(`${item.nome_urna} ${item.resumo_trajetoria}`);
      if (!texto.includes(busca)) return false;
    }
    return true;
  });
}

function contadorCargo(dados, cargo, rotulo) {
  const lista = dados.filter((item) => item.cargo.toUpperCase() === cargo);
  const contar = (raca) => lista.filter((item) => item.cor_raca_tse === raca).length;
  const pretas = contar("PRETA");
  const pardas = contar("PARDA");
  const brancas = contar("BRANCA");
  const outras = lista.length - pretas - pardas - brancas;
  return `<article class="contador">
    <h3>Total de candidatas a ${rotulo}</h3>
    <p class="contador__total">${lista.length}</p>
    <p class="contador__cores">Pretas: ${pretas} · Pardas: ${pardas} · Brancas: ${brancas}${outras ? ` · Outras: ${outras}` : ""}</p>
  </article>`;
}

function renderizarContadores(dados) {
  $("#contadores").innerHTML =
    contadorCargo(dados, "DEPUTADO ESTADUAL", "deputada estadual") +
    contadorCargo(dados, "DEPUTADO FEDERAL", "deputada federal");
  $("#total-encontrado").textContent = `${dados.length} ${dados.length === 1 ? "candidata encontrada" : "candidatas encontradas"}`;
}

function renderizarRedes(redes) {
  if (!redes?.length) return "";
  return redes.map((rede) => `<a class="rede" href="${escapar(rede.url)}" target="_blank" rel="noopener noreferrer">${escapar(rede.nome)}</a>`).join("");
}

function renderizarDetalhes(item) {
  const blocos = [];
  if (item.regiao_atuacao) blocos.push(`<h4>Região de atuação</h4><p>${escapar(item.regiao_atuacao)}</p>`);
  if (item.atuacao_documentada) blocos.push(`<h4>Atuação documentada</h4><p>${escapar(item.atuacao_documentada)}</p>`);
  if (item.trajetoria_declarada) blocos.push(`<h4>Trajetória declarada</h4><p>${escapar(item.trajetoria_declarada)}</p>`);
  if (item.historico?.length) {
    const itens = item.historico.map((linha) => `<li>${Object.values(linha).filter(Boolean).map(escapar).join(" · ")}</li>`).join("");
    blocos.push(`<h4>Histórico eleitoral disponível no TSE</h4><ul>${itens}</ul>`);
  }
  if (item.fontes?.length) {
    const fontes = item.fontes.map((url, indice) => `<li><a href="${escapar(url)}" target="_blank" rel="noopener noreferrer">Fonte ${indice + 1}</a></li>`).join("");
    blocos.push(`<h4>Fontes da curadoria</h4><ul>${fontes}</ul>`);
  }
  return blocos.join("");
}

function criarCard(item) {
  const card = $("#modelo-card").content.cloneNode(true);
  const foto = card.querySelector(".card-candidata__foto");
  foto.src = item.foto;
  foto.alt = `Foto oficial de ${item.nome_urna}`;
  card.querySelector(".card-candidata__nome").textContent = item.nome_urna;
  card.querySelector(".card-candidata__identificacao").textContent = `${item.cargo_feminino} · ${item.partido} · nº ${item.numero}`;
  card.querySelector(".card-candidata__raca").textContent = item.cor_raca_tse.charAt(0) + item.cor_raca_tse.slice(1).toLowerCase();
  card.querySelector(".card-candidata__resumo").textContent = item.resumo_trajetoria;
  card.querySelector(".card-candidata__pautas").innerHTML = item.pautas.map((pauta) => `<span class="pauta">${escapar(pauta)}</span>`).join("");
  card.querySelector(".card-candidata__redes").innerHTML = renderizarRedes(item.redes);
  card.querySelector(".detalhes__conteudo").innerHTML = renderizarDetalhes(item);
  return card;
}

function renderizar() {
  const dados = aplicarFiltros();
  renderizarContadores(dados);
  const lista = $("#lista-candidatas");
  lista.replaceChildren(...dados.map(criarCard));
  $("#sem-resultados").hidden = dados.length > 0;
}

function atualizarOpcoes() {
  preencherSelect("#filtro-cargo", opcoesDaPagina("cargo"), "Todos os cargos");
  preencherSelect("#filtro-partido", opcoesDaPagina("partido"), "Todos os partidos");
  preencherSelect("#filtro-pauta", opcoesDaPagina("pautas"), "Todas as pautas");
  preencherSelect("#filtro-raca", opcoesDaPagina("cor_raca_tse"), "Todas as autodeclarações");
}

function limparFiltros(renderizarAgora = true) {
  estado.filtros = { cargo: "", partido: "", pauta: "", raca: "", busca: "" };
  ["#filtro-cargo", "#filtro-partido", "#filtro-pauta", "#filtro-raca", "#filtro-busca"].forEach((id) => { $(id).value = ""; });
  if (renderizarAgora) renderizar();
}

function mudarPagina(pagina) {
  estado.pagina = pagina;
  $$(".navegacao__item").forEach((botao) => botao.classList.toggle("ativo", botao.dataset.pagina === pagina));
  const metodologia = pagina === "metodologia";
  $("#explorador").hidden = metodologia;
  $("#metodologia").hidden = !metodologia;
  if (metodologia) return;
  $("#titulo-pagina").textContent = pagina === "negras" ? "Candidatas negras" : "Todas as candidatas";
  $("#grupo-raca").hidden = pagina !== "todas";
  atualizarOpcoes();
  limparFiltros(false);
  renderizar();
}

function mostrarAviso(texto) {
  const aviso = $("#aviso");
  aviso.textContent = texto;
  aviso.hidden = false;
  window.setTimeout(() => { aviso.hidden = true; }, 2800);
}

async function compartilhar() {
  const dados = { title: document.title, text: "Mulheres e Representação Política 2026", url: location.href };
  try {
    if (navigator.share) await navigator.share(dados);
    else {
      await navigator.clipboard.writeText(location.href);
      mostrarAviso("Link copiado.");
    }
  } catch (erro) {
    if (erro.name !== "AbortError") mostrarAviso("Não foi possível copiar o link.");
  }
}

async function iniciar() {
  const respostaManifesto = await fetch("data/manifest.json");
  if (!respostaManifesto.ok) throw new Error("Falha ao carregar a base de candidatas.");
  const arquivos = await respostaManifesto.json();
  const respostas = await Promise.all(arquivos.map((arquivo) => fetch(`data/${arquivo}`)));
  if (respostas.some((resposta) => !resposta.ok)) throw new Error("Falha ao carregar a base de candidatas.");
  estado.dados = (await Promise.all(respostas.map((resposta) => resposta.json()))).flat();
  atualizarOpcoes();
  renderizar();

  $$(".navegacao__item").forEach((botao) => botao.addEventListener("click", () => mudarPagina(botao.dataset.pagina)));
  [["#filtro-cargo", "cargo"], ["#filtro-partido", "partido"], ["#filtro-pauta", "pauta"], ["#filtro-raca", "raca"]].forEach(([id, campo]) => {
    $(id).addEventListener("change", (evento) => { estado.filtros[campo] = evento.target.value; renderizar(); });
  });
  $("#filtro-busca").addEventListener("input", (evento) => { estado.filtros.busca = evento.target.value.trim(); renderizar(); });
  $("#limpar-filtros").addEventListener("click", () => limparFiltros());
  $("#compartilhar").addEventListener("click", compartilhar);
}

iniciar().catch((erro) => {
  $("#lista-candidatas").innerHTML = `<div class="sem-resultados"><h2>Não foi possível abrir a plataforma</h2><p>${escapar(erro.message)}</p></div>`;
});
