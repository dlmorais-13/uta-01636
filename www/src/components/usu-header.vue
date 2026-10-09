<template>
    <header>
        <div id="site-header" class="d-none d-lg-block">
            <UsuQuickLinks :on-open-search-overlay="() => searchOverlayOpen = true"></UsuQuickLinks>

            <div class="container d-none d-lg-block">
                <div class="row">
                    <div class="header-brand-wrapper-inline pt-2 ml-lg-3 has-unit">
                        <a class="align-self-center" href="https://www.usu.edu/">
                            <img class="" src="/images/utah-state-logo.svg" width="300" height="29"
                                alt="Utah State University logo">
                        </a>
                        <div class="brand-inline ml-3 pl-3">
                            <router-link class="header-brand" to="/">
                                System Name
                                <!-- Landscape Architecture & Environmental Planning -->
                            </router-link>
                            <a class="header-sub-brand" href="https://qanr.usu.edu/laep/">
                                Department Responsible
                                <!-- S.J. & Jessie E. Quinney College of Agriculture & Natural Resources -->
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <UsuSearchOverlay :open="searchOverlayOpen" :on-close="() => searchOverlayOpen = false"></UsuSearchOverlay>
    </header>

    <UsuMainNav :on-open-search-overlay="() => searchOverlayOpen = true"></UsuMainNav>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import UsuMainNav from './usu-main-nav.vue';
import UsuQuickLinks from './usu-quick-links.vue';
import UsuSearchOverlay from './usu-search-overlay.vue';

const searchOverlayOpen = ref(false)
</script>

<style>
header .header-brand-collapsed {
    background-color: var(--usu-aggie-blue);
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    align-items: center;
    justify-content: center;
}

header .header-brand-collapsed img.img-fluid {
    width: 100%;
    max-width: 180px;
}

header .header-brand {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    font-size: 1.2rem;
    color: var(--usu-white);
    line-height: 1.5rem;
    text-align: center;
}

#site-header .header-sub-brand {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
}

@media (min-width: 576px) {
    header .header-brand {
        font-size: 1.3rem;
        line-height: 1.6rem;
    }

    header .header-brand-collapsed img.img-fluid {
        max-width: 200px;
    }
}

@media (min-width: 768px) {
    header .header-brand {
        font-size: 1.5rem;
        line-height: 1.8rem;
    }

    header .header-brand-collapsed img.img-fluid {
        max-width: 220px;
    }
}

#site-header .header-brand-wrapper-inline img.img-fluid {
    width: 100%;
    width: 350px;
    max-width: 350px;
}

#site-header {
    background-color: var(--usu-aggie-blue);
}

#site-header-nav {
    background-color: var(--usu-aggie-blue);
    padding: 0;
    margin: 0;
}

#site-header-nav>.collapse,
#site-header-nav>.collapsing {
    background-color: var(--usu-blue-darker);
    color: var(--usu-white);
}

#site-header .navbar-collapse {
    display: flex;
    justify-content: flex-end;
}

#site-header .nav-link {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    font-weight: 400;
    color: var(--usu-white);
    margin: 0;
}

#site-header .navbar .nav-link:hover,
#site-header .navbar .nav-link:focus {
    background-color: var(--usu-bright-light);
    text-decoration: none;
}

#site-header .nav-link[aria-expanded="true"] {
    background-color: var(--usu-blue-darker);
}

#site-header .navbar-nav>.active>a,
#site-header .navbar-nav>.active>a:focus {
    background-color: var(--usu-blue-darker);
}

#site-header .navbar-nav>.active>a:hover {
    background-color: var(--usu-bright-light);
}

#site-header-nav>.collapse a,
#site-header-nav>.collapsing a {
    color: var(--usu-gray);
}

#site-header-nav>.collapse a:hover,
#site-header-nav>.collapse a:focus,
#site-header-nav>.collapsing a:hover,
#site-header-nav>.collapsing a:focus {
    color: var(--usu-white);
    text-decoration: underline;
}

#site-header ::placeholder,
/* Chrome, Firefox, Opera, Safari 10.1+ */
#site-header :-ms-input-placeholder,
/* Internet Explorer 10-11 */
#site-header ::-ms-input-placeholder {
    /* Microsoft Edge */
    color: var(--usu-gray);
    opacity: .5;
    /* Firefox */
}

#site-header input:-webkit-autofill,
#site-header input:-webkit-autofill:hover,
#site-header input:-webkit-autofill:focus,
#site-header input:-webkit-autofill:active {
    -webkit-animation: autofill 0s forwards;
    animation: autofill 0s forwards;
    color: var(--usu-white);
}

#site-header #site-header-nav input {
    background-color: transparent;
    border: none;
    color: var(--usu-white);
    border-radius: 0;
    border-bottom: 2px solid var(--usu-blue);
}

#site-header #site-header-nav input:focus {
    outline: none;
    box-shadow: none;
}

#site-header #site-header-nav .input-group .btn {
    color: var(--usu-gray);
    border: none;
    border-radius: 0;
    border-bottom: 2px solid var(--usu-blue);
}

#site-header #site-header-nav .input-group .btn:hover {
    color: var(--usu-white);
}


@media screen and (min-width: 992px) {
    #site-header .navbar .container {
        position: relative;
    }

    #site-header .navbar .collapse {
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        z-index: 1;
    }

    #site-header .header-brand-wrapper {
        min-height: 120px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        align-items: flex-start;
        justify-content: center;
    }

    #site-header .header-brand-wrapper-inline.has-unit img {
        max-width: 220px;
    }

    #site-header .header-brand-wrapper-inline {
        min-height: 120px;
        display: flex;
        flex-direction: row;
    }

    #site-header .header-brand-wrapper-inline img.img-fluid {
        margin-bottom: 1px;
    }

    #site-header .header-brand {
        font-size: 1.4rem;
        line-height: 1.7rem;
        color: var(--usu-gray-title);
        text-align: left;
    }

    #site-header .header-brand:hover {
        color: var(--usu-white);
    }

    #site-header .header-sub-brand {
        font-size: 1.1rem;
        line-height: 1.4rem;
        color: var(--usu-white);
    }

    #site-header .brand-inline {
        display: flex;
        align-self: center;
        flex-direction: column;
        justify-content: center;
        color: var(--usu-gray);
        border-left: 2px solid var(--usu-gray);
    }

    #site-header .brand-inline:hover {
        color: var(--usu-white);
    }
}

@media screen and (min-width: 1200px) {
    #site-header .header-brand-wrapper-inline img.img-fluid {
        margin-top: 4px;
    }

    #site-header .header-brand-wrapper-inline.has-unit img.img-fluid {
        max-width: 260px;
    }

    #site-header .header-brand {
        font-size: 1.6rem;
        line-height: 2rem;
    }

    #site-header .header-sub-brand {
        font-size: 1.15rem;
        line-height: 1.4rem;

    }
}
</style>
