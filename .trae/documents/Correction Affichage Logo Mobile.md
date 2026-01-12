# Correction du Logo Coupé sur Mobile

Le problème d'affichage du logo (coupé en haut) sur mobile semble être dû à un manque d'espace ou à un positionnement incorrect dans l'en-tête (header) sur les petits écrans.

## Analyse

*   **Structure HTML :** Le logo est dans `.header-logo` à l'intérieur de `.brand`.
*   **Problème :** Sur mobile, la hauteur du conteneur parent (`.header` ou `.w-nav-brand`) est probablement insuffisante pour afficher le logo entier, ou le logo a une taille inadaptée.

## Solution Technique

Nous allons ajouter des règles CSS spécifiques dans `css/custom.css` pour ajuster la taille du logo et assurer qu'il s'affiche correctement sur mobile, sans affecter la version bureau.

### Actions à réaliser :

1.  **Modifier `css/custom.css`** :
    *   Ajouter une Media Query pour les écrans mobiles (`max-width: 479px` et `max-width: 767px`).
    *   Ajuster la propriété `height` ou `max-height` de `.header-logo` pour qu'elle s'adapte au conteneur.
    *   Ajuster le `padding` ou la `margin` si nécessaire pour centrer le logo verticalement.
    *   S'assurer que `object-fit: contain` est appliqué pour préserver les proportions.

### Code CSS Proposé :

```css
/* Correction Logo Mobile */
@media screen and (max-width: 767px) {
    .header-logo {
        height: auto; /* Laisser la hauteur s'adapter */
        max-height: 60px; /* Limiter la hauteur pour qu'il rentre dans la navbar */
        width: auto; /* Garder les proportions */
        object-fit: contain; /* S'assurer que l'image n'est pas rognée */
    }
    
    /* Ajustement optionnel du conteneur si nécessaire */
    .w-nav-brand {
        padding-top: 5px;
        padding-bottom: 5px;
        display: flex;
        align-items: center;
    }
}
```

Cela permettra au logo de s'afficher entièrement sans être coupé, tout en restant proportionné dans la barre de navigation mobile.
