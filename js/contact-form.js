(function () {
    // -------------------------------------------------------------------------
    // ETAPE 1 : Configuration EmailJS
    // Créez un compte gratuit sur https://www.emailjs.com/
    // Remplacez les valeurs ci-dessous par les vôtres.
    // -------------------------------------------------------------------------

    // Votre "Public Key" (trouvable dans Account > API Keys)
    const PUBLIC_KEY = 'VOTRE_PUBLIC_KEY_ICI';

    // Votre "Service ID" (créez un service "Gmail" dans EmailJS)
    const SERVICE_ID = 'VOTRE_SERVICE_ID_ICI';

    // Votre "Template ID" (créez un template d'email)
    const TEMPLATE_ID = 'VOTRE_TEMPLATE_ID_ICI';

    // -------------------------------------------------------------------------

    // Vérification que le SDK est chargé
    if (typeof emailjs === 'undefined') {
        console.error("Le SDK EmailJS n'est pas chargé. Vérifiez le fichier contact-us.html");
        return;
    }

    // Initialisation
    try {
        emailjs.init(PUBLIC_KEY);
    } catch (e) {
        console.warn("EmailJS non configuré (Public Key manquante). Le script ne fonctionnera pas tant que la clé n'est pas ajoutée.");
    }

    window.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('wf-form-Email-Form');

        if (!form) {
            console.log("Formulaire non trouvé sur cette page.");
            return;
        }

        form.addEventListener('submit', function (event) {
            event.preventDefault();

            // Indicateur de chargement sur le bouton
            const submitBtn = form.querySelector('input[type="submit"]');
            const originalBtnText = submitBtn.value;
            submitBtn.value = "Envoi en cours...";
            submitBtn.disabled = true;

            // Récupération des valeurs du formulaire
            // Assurez-vous que vos variables de template EmailJS ({{from_name}}, etc.) sont correctes.
            const templateParams = {
                to_email: 'tomviseur7@gmail.com', // Cette variable doit être utilisée dans le champ "To" de votre Template EmailJS si vous voulez rendre dynamique, sinon configurez-le directement dans EmailJS
                from_name: document.getElementById('Name').value + ' ' + document.getElementById('Last-Name').value,
                from_email: document.getElementById('Email').value,
                subject: document.getElementById('Subject').value,
                message: document.getElementById('field').value // Le champ message s'appelle "field" dans votre HTML
            };

            // Envoi
            emailjs.send(SERVICE_ID, TEMPLATE_ID, templateParams)
                .then(function () {
                    console.log('Email envoyé avec succès !');
                    submitBtn.value = originalBtnText;
                    submitBtn.disabled = false;

                    // Comportement visuel Webflow : Cacher le form, Afficher le message de succès
                    form.style.display = 'none';
                    const successMessage = form.parentElement.querySelector('.w-form-done');
                    if (successMessage) successMessage.style.display = 'block';

                }, function (error) {
                    console.error('Erreur lors de l\'envoi :', error);
                    submitBtn.value = originalBtnText;
                    submitBtn.disabled = false;

                    // Comportement visuel Webflow : Afficher le message d'erreur
                    const errorMessage = form.parentElement.querySelector('.w-form-fail');
                    if (errorMessage) errorMessage.style.display = 'block';

                    // Facultatif : alert pour debugging si les clés ne sont pas mises
                    if (error.text && error.text.includes("The user_id param")) {
                        alert("Erreur de configuration EmailJS : La Public Key semble manquante ou incorrecte dans js/contact-form.js");
                    }
                });
        });
    });
})();
