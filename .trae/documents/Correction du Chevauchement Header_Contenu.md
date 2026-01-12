# Correction de l'Affichage des Pages Légales

Le problème d'affichage (titre coupé) est dû au fait que la barre de navigation (header) est probablement fixée en haut de page (`position: fixed` ou `sticky`), et que le contenu des pages légales passe en dessous car il n'a pas assez de marge supérieure.

## Solution Technique

Nous allons ajuster le CSS dans `css/custom.css` pour augmenter la marge supérieure (`margin-top`) du conteneur `.legal-content`.

### Actions à réaliser :

1.  **Modifier `css/custom.css`** :
    *   Augmenter la marge supérieure de `60px` à **`150px`** pour la version bureau (Desktop).
    *   Ajouter des ajustements pour les versions tablettes et mobiles (Responsive) afin d'éviter un espace vide trop grand sur les petits écrans.
    *   Ajouter `position: relative` et `z-index` pour s'assurer que le contenu reste bien accessible et ne passe pas sous d'autres éléments décoratifs.

### Code CSS Proposé :

```css
.legal-content {
    /* ... propriétés existantes ... */
    margin: 150px auto 60px; /* Augmentation significative de la marge haute */
    position: relative;
    z-index: 5;
}

/* Ajustements Responsive */
@media (max-width: 991px) {
    .legal-content {
        margin-top: 120px;
    }
}

@media (max-width: 768px) {
    .legal-content {
        margin: 100px 15px 30px;
    }
}
```

Cela garantira que le titre "Politique de Confidentialité" et "Mentions Légales" s'affiche entièrement sous la barre de navigation.
