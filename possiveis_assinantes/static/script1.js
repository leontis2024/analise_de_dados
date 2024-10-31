localStorage.setItem("terminou", null);
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    // Limpar mensagens de erro
    const erros = document.querySelectorAll(".erro");
    erros.forEach((erro) => (erro.textContent = ""));

    let valid = true;

    // Validação das perguntas
    const artePreferida = document.querySelector(
      'input[name="arte_interesse"]:checked'
    );
    if (!artePreferida) {
      document.getElementById("erro-arte-interesse").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }

    const frequenciaMuseus = document.querySelector(
      'input[name="frequencia_museus"]:checked'
    );
    if (!frequenciaMuseus) {
      document.getElementById("erro-frequencia-museu").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }

    const cursoArte = document.querySelector(
      'input[name="curso_arte"]:checked'
    );
    if (!cursoArte) {
      document.getElementById("erro-curso-arte").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }

    const segueArtistas = document.querySelector(
      'input[name="segue_artistas"]:checked'
    );
    if (!segueArtistas) {
      document.getElementById("erro-segue-artista").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }

    const experienciaMuseu = document.querySelector(
      'input[name="experiencia_museu"]:checked'
    );
    if (!experienciaMuseu) {
      document.getElementById("erro-exeperiencia_museu").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }

    const usouApp = document.querySelector('input[name="usou_app"]:checked');
    if (!usouApp) {
      document.getElementById("erro-usou_app").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }

    const atracaoMuseu = document.querySelector(
      'input[name="atracao_museu"]:checked'
    );

    if (!atracaoMuseu) {
      document.getElementById("erro-atracao-museu").textContent =
        "Por favor, selecione uma opção.";
      valid = false;
    }
    let infoObras = null;
    if (atracaoMuseu.value != "Não visito") {
      infoObras = document.querySelector('input[name="info_obras"]:checked');
      if (!infoObras) {
        document.getElementById("erro-info-obras").textContent =
          "Por favor, selecione uma opção.";
        valid = false;
      }
    }
    let infobusca = null;
    if (
      infoObras &&
      infoObras.value != "Não, acredito que o que tem no museu é o suficiente"
    ) {
      infobusca = document.querySelector('input[name="info_busca"]:checked');
      if (!infobusca) {
        document.getElementById("erro-info-busca").textContent =
          "Por favor, selecione uma opção.";
        valid = false;
      }
    }
    let ondeBusca = null;
    if (infobusca && infobusca.value != "Não, apenas me conformo") {
      ondeBusca = document.querySelector('input[name="onde_busca"]:checked');
      if (!ondeBusca) {
        document.getElementById("erro-onde-busca").textContent =
          "Por favor, selecione uma opção.";
        valid = false;
      }
      const achaInformacao = document.querySelector(
        'input[name="acha_informacao"]:checked'
      );
      if (!achaInformacao) {
        document.getElementById("erro-acha-informacao").textContent =
          "Por favor, selecione uma opção.";
        valid = false;
      }
    }

    if (valid) {
      if (form.getAttribute("action") == "/submit") {
        localStorage.setItem("terminou", true);
      } else {
        localStorage.setItem("terminou", false);
      }
      form.submit();
    }
  });

  handleChange(
    "atracao_museu",
    "aditional-question",
    "Não visito",
    "/não_interesse"
  );
  handleChange(
    "info_obras",
    "aditional-question1",
    "Não, acredito que o que tem no museu é o suficiente",
    "/não_interesse"
  );
  handleChange(
    "info_busca",
    "aditional-question2",
    "Não, apenas me conformo",
    "/não_interesse"
  );
});

function handleChange(radioName, questionId, exclusionValue, redirectUrl) {
  const radios = document.querySelectorAll(`input[name="${radioName}"]`);
  const additionalQuestions = document.getElementById(questionId);

  radios.forEach(function (radio) {
    radio.addEventListener("change", function (event) {
      if (event.target.value === exclusionValue) {
        additionalQuestions.style.display = "none";
      } else {
        additionalQuestions.style.display = "block";
      }
    });
  });
}
