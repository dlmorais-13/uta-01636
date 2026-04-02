<template>
    <nav id="master-nav" class="navbar nav-white navbar-expand-lg sticky-top px-0" aria-label="Main menu">
        <div class="container pt-0 px-0">
            <div id="offcanvas-backdrop" :class="offcanvasOpen && 'backdrop'" tabindex="-1" aria-hidden="true"
                @click="offcanvasOpen = quicklinksOpen = false"></div>

            <div class="nav-brand-wrapper pl-0">
                <div class="d-flex flex-column justify-content-center ml-2 ml-sm-3 mr-2 my-3 pr-1">
                    <a href="https://www.usu.edu">
                        <img width="80" height="61" src="/images/u-state-logo.svg" class="img-fluid pr-1 pr-sm-2"
                            alt="UState logo">
                    </a>
                </div>
                <router-link class="nav-brand py-3" to="/">
                    <div>System Name</div>
                </router-link>
                <button class="navbar-toggler custom-toggler mr-sm-2 px-2" type="button" data-toggle="offcanvas"
                    aria-haspopup="dialog" @click="offcanvasOpen = true">
                    <span class="sr-only">Open main menu</span><span class="navbar-toggler-icon"></span>
                </button>
            </div>

            <div class="navbar-collapse offcanvas-collapse" id="main-navbar" role="dialog" aria-label="Main navigation"
                :class="offcanvasOpen && 'open'">
                <div class="offcanvas-header px-2">
                    <button type="button" class="btn my-2 offcanvas-close" data-toggle="offcanvas"
                        @click="offcanvasOpen = false">
                        <svg class="svg-inline--fa fa-xmark mr-1" aria-hidden="true" focusable="false" data-prefix="fas"
                            data-icon="xmark" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"
                            data-fa-i2svg="">
                            <path fill="currentColor"
                                d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z">
                            </path>
                        </svg>Close
                    </button>

                    <button type="button" id="offcanvas-search-btn" class="btn search-btn ml-auto my-2"
                        @click="onOpenSearchOverlay()" aria-haspopup="dialog"><span class="sr-only">Open
                            search</span><svg class="svg-inline--fa fa-magnifying-glass fa-lg" aria-hidden="true"
                            focusable="false" data-prefix="fas" data-icon="magnifying-glass" role="img"
                            xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" data-fa-i2svg="">
                            <path fill="currentColor"
                                d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z">
                            </path>
                        </svg><!-- <i class="fa-solid fa-magnifying-glass fa-lg"></i> -->
                    </button>
                </div>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <router-link class="nav-link" to="/">Home</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/map">Map</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/admin">Admin</router-link>
                    </li>
                </ul>
                <ul class="navbar-nav navbar-global py-3">
                    <li class="nav-item dropdown dropdown-hover">
                        <a class="nav-link dropdown-toggle" id="offcanvas-quicklinks" data-toggle="dropdown"
                            @click="quicklinksOpen = true" role="button" aria-haspopup="true" aria-expanded="false"><svg
                                class="svg-inline--fa fa-list mb-1 mr-2" aria-hidden="true" focusable="false"
                                data-prefix="fas" data-icon="list" role="img" xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 512 512" data-fa-i2svg="">
                                <path fill="currentColor"
                                    d="M40 48C26.7 48 16 58.7 16 72l0 48c0 13.3 10.7 24 24 24l48 0c13.3 0 24-10.7 24-24l0-48c0-13.3-10.7-24-24-24L40 48zM192 64c-17.7 0-32 14.3-32 32s14.3 32 32 32l288 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L192 64zm0 160c-17.7 0-32 14.3-32 32s14.3 32 32 32l288 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-288 0zm0 160c-17.7 0-32 14.3-32 32s14.3 32 32 32l288 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-288 0zM16 232l0 48c0 13.3 10.7 24 24 24l48 0c13.3 0 24-10.7 24-24l0-48c0-13.3-10.7-24-24-24l-48 0c-13.3 0-24 10.7-24 24zM40 368c-13.3 0-24 10.7-24 24l0 48c0 13.3 10.7 24 24 24l48 0c13.3 0 24-10.7 24-24l0-48c0-13.3-10.7-24-24-24l-48 0z">
                                </path>
                            </svg><!-- <i class="fas fa-list mr-2 mb-1"></i> -->Quick Links <svg
                                class="svg-inline--fa fa-angle-right mb-1 ml-auto" aria-hidden="true" focusable="false"
                                data-prefix="fas" data-icon="angle-right" role="img" xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 320 512" data-fa-i2svg="">
                                <path fill="currentColor"
                                    d="M278.6 233.4c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L210.7 256 73.4 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160z">
                                </path>
                            </svg><!-- <i class="fas fa-angle-right ml-auto mb-1"></i> --></a>
                        <div class="offcanvas-collapse-sub" :class="quicklinksOpen && 'open'">
                            <div class="offcanvas-header px-2">
                                <button type="button" class="btn my-2 offcanvas-back" @click="quicklinksOpen = false">
                                    <svg class="svg-inline--fa fa-times mr-1" aria-hidden="true" focusable="false"
                                        data-prefix="fas" data-icon="times" role="img"
                                        xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" data-fa-i2svg="">
                                        <path fill="currentColor"
                                            d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z">
                                        </path>
                                    </svg>Close
                                </button>
                                <div class="align-self-center mx-3">Quick Links</div>
                            </div>
                            <ul class="dropdown-menu show" aria-labelledby="offcanvas-quicklinks">
                                <li><a class="dropdown-item" href="https://www.usu.edu/apply/">Apply</a></li>
                                <li><a class="dropdown-item" href="https://www.usu.edu/visit/">Visit</a></li>
                                <li><a class="dropdown-item" href="https://www.usu.edu/advancement/">Give</a></li>
                                <li><a class="dropdown-item" href="https://www.usu.edu/calendar/">Calendar</a></li>
                                <li><a class="dropdown-item" href="https://www.usu.edu/azindex/">A-Z Index</a></li>
                                <li><a class="dropdown-item" href="https://directory.usu.edu/">Directory</a></li>
                                <li><a class="dropdown-item" href="https://library.usu.edu/">Libraries</a></li>
                            </ul>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="https://www.usu.edu/myusu/"><svg
                                class="svg-inline--fa fa-user mb-1 mr-2" aria-hidden="true" focusable="false"
                                data-prefix="fas" data-icon="user" role="img" xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 448 512" data-fa-i2svg="">
                                <path fill="currentColor"
                                    d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304l-91.4 0z">
                                </path>
                            </svg><!-- <i class="fas fa-user mr-2 mb-1"></i> -->MyUSU</a>
                    </li>
                </ul>
            </div>

        </div>
    </nav>
</template>

<script>
export default {
    data() {
        return {
            offcanvasOpen: false,
            quicklinksOpen: false
        }
    },

    props: {
        onOpenSearchOverlay: {
            type: Function,
            default: () => { console.warning('usu-quick-links function to open search overlay not defined.') }
        }
    }
}
</script>

<style>
/* Main Navigation Bar */
#master-nav {
    background-color: var(--usu-aggie-blue);
    padding-top: 0;
    padding-bottom: 0;
    /*box-shadow: 0 0.5rem 0.5rem -0.25rem rgba(17,17,17,.5);  */
}

#master-nav>div.container {
    padding-left: 0;
}

/* Background of dropdowns */
#master-nav .navbar-nav {
    background-color: var(--usu-white);
    padding: 30px 0;
}

#master-nav .nav-link {
    display: flex;
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    font-size: 1.2rem;
    padding: .5rem 0;
    margin: 0 25px;
    border-bottom: 2px solid var(--usu-gray-light);
    color: var(--usu-black-light);
}

#master-nav .navbar-global {
    background-color: var(--usu-blue-darker);
}

#master-nav .navbar-global .nav-link {
    color: var(--usu-gray);
    border-bottom: 1px solid var(--usu-blue);
}

#master-nav .navbar-global .nav-link:hover {
    color: var(--usu-white);
}

#master-nav .dropdown-toggle::after {
    display: none;
}

#master-nav .nav-link svg {
    align-self: center;
}

#master-nav .nav-link .fa-angle-right {
    font-size: 1.6rem;
}

#master-nav .nav-link .fa-angle-right {
    margin-left: auto;
}

#master-nav .navbar-toggler {
    margin-bottom: .55rem;
    margin-top: .55rem;
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
}

#master-nav .navbar-toggler:hover,
#master-nav .navbar-toggler:focus {
    background-color: var(--usu-bright-light);
    text-decoration: none;
}

/* Dropdown */
#master-nav .dropdown-menu {
    font-size: 1.1rem;
    background-color: var(--usu-white);
    border: none;
    border-radius: 0;
    padding-top: 15px;
    padding-bottom: 15px;
}

#master-nav .dropdown-menu ul {
    padding-left: 0;
}

#master-nav .dropdown-menu li {
    list-style: none;
    margin-bottom: .25rem;
}

#master-nav .dropdown-menu li a {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--usu-black-light);
    white-space: normal;
}

#master-nav .dropdown-menu a:hover,
#master-nav .dropdown-menu a:focus {
    color: var(--usu-info);
    background-color: transparent;
    text-decoration: underline !important;
}

#master-nav .dropdown-divider {
    border-bottom: 1px solid var(--usu-gray-light) !important;
}

/* Mega-menu styles */
#master-nav .mega-menu {
    position: static;
}

#master-nav .mega-menu .dropdown-menu {
    border-radius: 0;
    padding-top: 30px;
    padding-left: 10px;
    padding-right: 10px;
    width: 100%;
}

#master-nav .mega-menu .dropdown-menu li a {
    padding-left: 0;
    padding-bottom: .25rem;
    padding-top: .25rem;
    width: 100%;
    display: block;
}

#master-nav .mega-menu .col-title,
#master-nav .dropdown-menu .col-title,
#master-nav .dropdown-menu.multi-column .col-title {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    font-size: 1.4rem;
    font-weight: 400;
    color: var(--usu-gray-dark);
    margin-bottom: 10px;
}

#master-nav .dropdown-flex-col.border {
    border: 0 !important;
    border-bottom: 1px solid var(--usu-gray-light) !important;
    margin-bottom: 15px;
    padding-bottom: 15px;
}

/* Multi column dropdown */
#master-nav .dropdown-menu.multi-column {
    border-radius: 0;
    padding-bottom: 30px;
    padding-top: 30px;
    min-width: 100%;
    padding-left: 10px;
    padding-right: 10px;
}

#master-nav .dropdown-menu.multi-column li a {
    padding-left: 0;
}

#master-nav .nav-brand-wrapper {
    display: flex;
    flex-grow: 1;
    justify-content: space-between;
    padding-left: 3.5rem;
    padding-right: 3.5rem;
}

#master-nav .nav-brand-wrapper .search-btn {
    color: var(--usu-gray);
    border: none;
    background: none;
}

#master-nav .nav-brand-wrapper .search-btn:hover {
    color: var(--usu-white);
}

#master-nav .nav-brand {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    display: flex;
    flex-grow: 1;
    align-self: center;
    justify-content: center;
    text-align: center;
    font-size: 1.2rem;
    color: var(--usu-white);
    line-height: 1.5rem;
}

@media (min-width: 576px) {
    #master-nav .nav-brand {
        font-size: 1.3rem;
    }
}

@media (min-width: 768px) {
    #master-nav .nav-brand {
        font-size: 1.5rem;
    }
}

/*@media (min-width: 992px){
	#master-nav .mega-menu .dropdown-menu li a {
		display: inline;
	}
}*/
/* nav button */
#master-nav a.nav-link.nav-btn {
    border: none;
    color: var(--usu-white);
    font-weight: bold;
    font-size: 1.167rem;
    padding: .75rem 2rem .6rem;
    margin: 0;
}

#master-nav a.nav-link.nav-btn:not(:first-child) {
    margin-top: .5rem;
}

#master-nav a.nav-link.nav-btn {
    border-bottom: 3px solid transparent;
}

#master-nav a.nav-link.nav-btn:hover {
    color: var(--usu-white);
    border-bottom: 3px solid var(--usu-white);
}

@media (min-width: 992px) {
    #master-nav a.nav-link.nav-btn.nav-btn {
        margin-left: 1rem;
    }

    #master-nav a.nav-link.nav-btn:not(:first-child) {
        margin-top: 0px;
    }
}

/* Offcanvas */
#master-nav .offcanvas-header {
    display: flex;
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    font-size: 1.3rem;
    color: var(--usu-white);
}

/* to remove !!!!*/
#master-nav .offcanvas-header a {
    display: flex;
    font-size: 1.3rem;
    color: var(--usu-gray);
    text-decoration: none;
}

/* to remove !!!!*/
#master-nav .offcanvas-header a:hover {
    color: var(--usu-white);
}

/* to remove !!!!*/
#master-nav .offcanvas-header .offcanvas-back {
    justify-content: space-between;
    flex-grow: 1;
}

/* to remove !!!!*/
#master-nav .offcanvas-close .fa-times {
    /*font-size: 1.5rem;
	position: relative;
	bottom: .1rem;*/
}

/* to remove after upadte? !!!!*/
#master-nav .offcanvas-header button {
    flex-grow: 0 !important;
}

#master-nav .btn.offcanvas-close,
#master-nav .btn.offcanvas-back,
#master-nav .offcanvas-header .btn.search-btn {
    color: var(--usu-white);
    background-color: var(--usu-blue-darker);
    font-size: 1.3rem;
}

#master-nav .btn.offcanvas-close:hover,
#master-nav .btn.offcanvas-back:hover,
#master-nav .offcanvas-header .btn.search-btn:hover {
    background-color: var(--usu-bright-light);
}

#master-nav .btn.offcanvas-close:focus,
#master-nav .btn.offcanvas-back:focus,
#master-nav .offcanvas-header .btn.search-btn:focus {
    background-color: var(--usu-bright-light);
    text-decoration: none;
}

#master-nav.navbar-scroll {
    box-shadow: none;
}

#master-nav ::placeholder {
    /* Chrome, Firefox, Opera, Safari 10.1+ */
    color: var(--usu-gray);
    opacity: 1;
    /* Firefox */
}

#master-nav :-ms-input-placeholder {
    /* Internet Explorer 10-11 */
    color: var(--usu-gray);
}

#master-nav ::-ms-input-placeholder {
    /* Microsoft Edge */
    color: var(--usu-gray);
}

/* Backdrop for offcanvas*/
#offcanvas-backdrop {
    transition: opacity .5s;
    opacity: 0;
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    z-index: 998;
    background: rgba(0, 0, 0, .4);
    cursor: default;
    pointer-events: none;
}

#offcanvas-backdrop.backdrop {
    opacity: 1;
    pointer-events: all;
}

#master-nav .custom-toggler .navbar-toggler-icon {
    background-image: url("data:image/svg+xml;charset=utf8,%3Csvg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath stroke='rgba(248,248,250, 0.8)' stroke-width='4' stroke-linecap='round' stroke-miterlimit='10' d='M4 8h24M4 16h24M4 24h24'/%3E%3C/svg%3E");
}

.navbar-scroll {
    background-color: rgba(15, 36, 57, 0.4);
    transition: background-color 0.5s;
}

.custom-toggler .navbar-toggler-icon {
    background-image: url("data:image/svg+xml;charset=utf8,%3Csvg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath stroke='rgba(52,58,64, 0.8)' stroke-width='4' stroke-linecap='round' stroke-miterlimit='10' d='M4 8h24M4 16h24M4 24h24'/%3E%3C/svg%3E");
}

.custom-toggler.navbar-toggler {
    border: 0;
}

@media (max-width: 991.99px) {
    #master-nav .nav-link .fa-angle-down {
        transform: rotate(-90deg);
    }
}

@media (min-width: 992px) {
    #master-nav {
        background-color: var(--usu-blue-darker);
    }

    #master-nav {
        box-shadow: none;
        /*0 0.5rem 0.5rem -0.25rem rgba(17,17,17,.25)*/
    }

    #master-nav .navbar-nav {
        display: flex;
        flex-grow: 1;
        background-color: transparent;
        padding: 0;
    }

    #master-nav li.nav-item {
        display: flex;
    }

    #master-nav a.nav-link {
        background-color: transparent;
        border: none;
        align-self: stretch;
        border-bottom: 3px solid transparent;
        font-size: 1rem;
        font-weight: 400;
        color: var(--usu-white);
        margin: 0;
        padding: 0.75rem 0.75rem 0.6rem;
        white-space: nowrap;
    }

    /*#master-nav a.nav-link.activ {
		background-color: var(--usu-gray-dark);
		color: var(--usu-white);
	}*/
    #master-nav .nav-link:hover,
    #master-nav .nav-link:focus {
        border-bottom: 3px solid var(--usu-blue-light);
        /*border-top: 3px solid var(--usu-blue-darker); nav-blue*/
        /*background-color: var(--usu-blue-darker); nav-blue*/
        color: var(--usu-white);
    }

    #master-nav a.nav-link.dropdown-toggle[aria-expanded="true"] {
        border-bottom: 3px solid transparent;
        background-color: var(--usu-white);
        color: var(--usu-gray-darker);
    }

    /* nav-link dropdown icon */
    #master-nav .nav-link .fa-angle-down {
        font-size: 1rem;
    }

    #master-nav .dropdown-toggle[aria-expanded="true"] .fa-angle-down {
        transform: rotate(180deg);
    }

    /*#master-nav .nav-link .fa-angle-right, #master-nav .nav-link .fa-angle-left {
		font-size:1rem;
	}
	#master-nav .nav-link .fa-angle-right {
		margin-left: 8px;
	}*/
    /* Dropdown menu */
    #master-nav .dropdown-menu {
        min-width: 300px;
        background-color: var(--usu-white);
        border: 1px solid var(--usu-white);
        color: var(--usu-black-light);
        font-size: 1rem;
        margin-top: 6px;
        border-radius: 0;
        right: 0;
        box-shadow: 0 -6px 0 var(--usu-white), 0 1px 6px rgba(0, 0, 0, .2);
        background-clip: border-box;
    }

    #master-nav .dropdown-menu ul {
        line-height: 1.5rem;
    }

    #master-nav .dropdown-menu li a {
        font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
        font-size: 1rem;
        font-weight: 400;
        color: var(--usu-info);
        padding-top: 0.1rem;
        padding-bottom: 0.1rem;
    }

    #master-nav .dropdown-menu a {
        color: var(--usu-info);
    }

    #master-nav .dropdown-divider {
        border: 0 !important;
        border-top: 1px solid var(--usu-gray) !important;
    }

    /* Mega-menu styles */

    /* Fix display property of containers in megamenu and multi-column dropdown after upgrade to BS 4.5.3 */
    #master-nav .container .row {
        flex-grow: 1;
    }

    #master-nav .mega-menu .dropdown-menu li a {
        padding-bottom: 0.1rem;
        padding-top: 0.1rem;
    }

    /* Old code*/
    /*#master-nav .dropdown-menu .mega-menu {
		box-shadow: 0 0.5rem 0.25rem -0.25rem rgba(17,17,17,.2);
		padding-bottom: 30px;
		padding-top: 30px;
	}*/
    #master-nav .mega-menu .col-title,
    #master-nav .dropdown-menu .col-title,
    #master-nav .dropdown-menu.multi-column .col-title {
        font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
        font-size: 1.2rem;
        font-weight: 400;
        color: var(--usu-gray-darker);
    }

    #master-nav .h1,
    #master-nav .h2,
    #master-nav .h3,
    #master-nav .h4,
    #master-nav .h5,
    #master-nav .h6 {
        color: var(--usu-gray-darker);
    }

    #master-nav .dropdown-flex-col {
        display: flex;
        align-items: stretch;
        flex-direction: column;
    }

    #master-nav .dropdown-flex-col.border {
        border: 0 !important;
        border-right: 1px solid var(--usu-gray) !important;
        margin-bottom: 0;
    }

    #master-nav .dropdown-menu.multi-column {
        padding-bottom: 15px;
        padding-top: 15px;
    }

    #master-nav .dropdown-menu.multi-column-2 {
        min-width: 600px;
    }

    #master-nav .dropdown-menu.multi-column-3 {
        min-width: 710px;
    }

    /* Nav bar scroll */
    #master-nav.navbar-scroll {
        background-color: var(--usu-aggie-blue);
    }

    #master-nav.navbar-scroll a.nav-link.dropdown-toggle[aria-expanded="true"] {
        background-color: var(--usu-white);
        border-bottom: 3px solid var(--usu-white);
    }

    #master-nav.navbar-scroll .dropdown-menu {
        background-color: var(--usu-white);
        border: 1px solid var(--usu-white);
    }

    #master-nav .offcanvas-header,
    #master-nav .navbar-global,
    #master-nav .nav-brand-wrapper,
    #master-nav.nav-dropdown {
        display: none;
    }
}

@media (min-width: 1200px) {
    #master-nav a.nav-link {
        font-size: 1.125rem;
    }
}

@media (max-width: 991.98px) {
    .offcanvas-collapse {
        position: fixed;
        top: 0px;
        bottom: 0;
        left: 100%;
        width: 50%;
        overflow-y: auto;
        visibility: hidden;
        background-color: var(--usu-blue-darker);
        transition-timing-function: ease-in-out;
        transition-duration: .3s;
        transition-property: left, visibility;
        z-index: 999;
        box-shadow: -0.5rem 0 0.5rem 0.25rem rgba(17, 17, 17, .2);
    }

    .offcanvas-collapse.open {
        left: 50%;
        visibility: visible;
    }

    .offcanvas-collapse-sub {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 100%;
        width: 50%;
        overflow-y: auto;
        visibility: hidden;
        background-color: var(--usu-blue-darker);
        transition-timing-function: ease-in-out;
        transition-duration: .3s;
        transition-property: left, visibility;
        z-index: 1000;
    }

    .offcanvas-collapse-sub.open {
        left: 50%;
        visibility: visible;
    }

    .offcanvas-collapse-sub .offcanvas-header {
        justify-content: space-between;
    }
}

@media (max-width: 575.98px) {
    .offcanvas-collapse {
        width: 100%;
    }

    .offcanvas-collapse.open {
        left: 0;
        visibility: visible;
    }

    .offcanvas-collapse-sub {
        width: 100%;
    }

    .offcanvas-collapse-sub.open {
        left: 0;
        visibility: visible;
    }
}

/* Column Navigation Styles */
#sub-menu {
    font-family: 'Roboto Condensed', "Arial", "Helvetica", sans-serif;
    border: 1px solid var(--usu-gray-light);
    border-top: 10px solid var(--usu-blue-darker);
}

#sub-menu.floating {
    position: static;
    top: 50px;
    z-index: 999;
    background: var(--usu-white);
    right: 0;
    left: 0;
    margin-top: 0 !important;
    border-top: none;
    padding: .25rem 0 0 0;
}

#sub-menu.floating .sub-menu-brand {
    font-size: 1.2rem;
}

#sub-menu.floating .container {
    padding: 0 .75rem;
}

/*#master-nav.navbar-scroll + .floating {
	position: sticky;
}*/
#sub-menu.floating .sub-menu-brand-wrapper .navbar-toggler {
    order: 2;
    padding-right: 0;
}

.floating .navbar-toggler {
    padding-left: 0;
    margin-left: 0;
}

#sub-menu .navbar-toggler>.close {
    display: inline;
}

@media (min-width: 992px) {
    #sub-menu.floating {
        z-index: 999;
        background: var(--usu-white);
        right: 0;
        left: 0;
        margin-top: 0 !important;
        border-top: none;
        padding-top: .25rem;
        padding-bottom: .25rem;
    }

    #sub-menu.floating .container {
        padding-left: .6rem;
    }

    #sub-menu.floating .sub-menu-brand-wrapper .navbar-toggler {
        order: 1;
        padding-right: 1rem;
    }

    #sub-menu.floating .sub-menu-brand-wrapper .sub-menu-brand {
        order: 2;
    }
}

#sub-menu:not(.floating) .navbar-toggler.collapsed>.close,
#sub-menu:not(.floating) .navbar-toggler:not(.collapsed)>.navbar-toggler-icon {
    display: none;
}

#sub-menu .sub-menu-brand-wrapper {
    display: flex;
    flex-grow: 1;
    justify-content: space-between;
}

#sub-menu .sub-menu-brand {
    display: flex;
    flex-grow: 1;
    align-self: center;
    justify-content: center;
    text-align: center;
    font-size: 1.2rem;
    color: var(--usu-info);
    line-height: 1.5rem;
}

#sub-menu .sub-menu-brand:hover {
    color: var(--usu-bright-light);
}

#sub-menu ul li {
    border-top: 1px solid var(--usu-gray);
}

#sub-menu ul li:last-child {
    border-bottom: 1px solid var(--usu-gray);
}

#sub-menu ul li ul li:last-child {
    border-bottom: 0;
}

#sub-menu .nav-link {
    color: var(--usu-black-light);
    padding-right: 5px;
    padding-left: 20px;
}

#sub-menu .navbar-collapse>ul>li>a.nav-link {
    padding-left: 5px;
}

#sub-menu .navbar-collapse a.nav-link a.nav-link {
    padding-left: 20px;
}

#sub-menu a.nav-link:hover {
    background-color: var(--usu-gray-light);
}

#sub-menu li.nav-item.active {
    background-color: var(--usu-gray-lighter);
}

#sub-menu li.nav-item.active a {
    color: var(--usu-info);
}

#sub-menu .nav-link[aria-expanded="true"] .fa-angle-down {
    transform: rotate(180deg);
}

#sub-menu .nav {
    flex-direction: column;
}

#sub-menu .btn {
    margin: 0px;
}

#sub-menu .sub-nav-btn {
    display: flex;
    flex-direction: row;
    align-self: stretch;
}

@media (min-width: 576px) {
    #sub-menu .sub-menu-brand {
        font-size: 1.3rem;
    }
}

@media (min-width: 768px) {
    #sub-menu .sub-menu-brand {
        font-size: 1.4rem;
    }
}

@media (min-width: 992px) {
    #sub-menu {
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }

    #sub-menu .sub-menu-brand {
        font-size: 1.4rem;
        text-align: left;
        flex-grow: 0;
    }

    #sub-menu .sub-menu-brand-wrapper {
        flex-grow: 0;
        justify-content: flex-start;
    }

    #sub-menu .navbar-nav {
        flex-direction: column;
        width: 100%;
    }

    #sub-menu ul li {
        padding-left: 0;
        padding-right: 0;
    }
}
</style>