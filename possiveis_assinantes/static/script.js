document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form');
    const errorMessages = {
        idade: 'Por favor, selecione sua faixa etária.',
        renda_per_capita: 'Por favor, selecione sua renda per capita.',
        tempo_interesse: 'Por favor, selecione o tempo de interesse por arte.',
        arte_interesse: 'Por favor, selecione o tipo de arte que você se interessa'
    };

    form.addEventListener('submit', function (event) {
        event.preventDefault();  

        let isValid = true;

        const idade = document.querySelector('input[name="idade"]:checked');
        const rendaPerCapita = document.querySelector('input[name="renda_per_capita"]:checked');
        const tempoInteresse = document.querySelector('input[name="tempo_interesse"]:checked');


        const idadeError = document.getElementById('erro-idade');
        const rendaError = document.getElementById('erro-renda');
        const tempoInteresseError = document.getElementById('erro-tempo-interesse');
       

        // Valida idade
        if (!idade) {
            idadeError.textContent = errorMessages.idade;
            idadeError.style.color = 'red';
            isValid = false;
        } else {
            idadeError.textContent = '';
        }

        // Valida renda per capita
        if (!rendaPerCapita) {
            rendaError.textContent = errorMessages.renda_per_capita;
            rendaError.style.color = 'red';
            isValid = false;
        } else {
            rendaError.textContent = '';
        }

        console.log(tempoInteresse)

        // Valida tempo de interesse e decide o redirecionamento
        if (!tempoInteresse) {
            tempoInteresseError.textContent = errorMessages.tempo_interesse;
            tempoInteresseError.style.color = 'red';
            isValid = false;
        } else {
            tempoInteresseError.textContent = '';

            if (tempoInteresse.value == "Não me interesso") {
               form.setAttribute("action","")
            } 
        }

        if (isValid) {
            form.submit();
        }
    });
    
});


