<template>
    <Transition name="opacity">
        <section v-if="open" id="search-overlay" role="dialog" class="searchOpen" style="display: block;">
            <div class="close-btn">
                <button id="close-search" type="button" class="btn btn-lg ml-auto m-3 p-2" aria-label="Close"
                    @click="onClose()">
                    <span class="sr-only">Close search</span><svg class="svg-inline--fa fa-xmark" aria-hidden="true"
                        focusable="false" data-prefix="fas" data-icon="xmark" role="img" xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 384 512" data-fa-i2svg="">
                        <path fill="currentColor"
                            d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z">
                        </path>
                    </svg><!-- <i class="fa-solid fa-xmark"></i> -->
                </button>
            </div>
            <div class="container">
                <div class="row justify-content-center">
                    <form class="col-12 col-sm-10 col-lg-8" name="search_form" id="search_form" method="get"
                        action="https://www.usu.edu/search/">
                        <h2 class="my-5 text-bold">Search Utah State University:</h2>
                        <fieldset>
                            <legend class="sr-only">I want to search</legend>
                            <div class="custom-control custom-radio custom-control-inline">
                                <input type="radio" id="all_sites" name="search_type" class="custom-control-input"
                                    page="https://www.usu.edu/search/" checked="checked" value="Search USU sites">
                                <label class="custom-control-label h4 text-white" for="all_sites">All USU sites</label>
                            </div>
                            <div class="custom-control custom-radio custom-control-inline">
                                <input type="radio" id="people" name="search_type" class="custom-control-input"
                                    page="https://usu.edu/directory/" value="Search people">
                                <label class="custom-control-label h4 text-white" for="people">People</label>
                            </div>
                        </fieldset>
                        <div class="input-group my-3">
                            <label for="search_terms" class="sr-only">Search terms</label>
                            <input type="text" name="q" id="search_terms" class="form-control"
                                placeholder="Search USU sites" aria-label="Search">
                            <div class="input-group-append">
                                <button class="btn" type="submit" id="submit-search"><span class="sr-only">Submit
                                        search</span><svg class="svg-inline--fa fa-magnifying-glass fa-lg"
                                        aria-hidden="true" focusable="false" data-prefix="fas" data-icon="magnifying-glass"
                                        role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
                                        data-fa-i2svg="">
                                        <path fill="currentColor"
                                            d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z">
                                        </path>
                                    </svg><!-- <i class="fa-solid fa-magnifying-glass fa-lg"></i> --></button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </section>
    </Transition>
</template>

<script>
export default {
    props: {
        open: {
            type: Boolean,
            default: false
        },
        onClose: {
            type: Function,
            default: () => { console.warning('usu-search-overlay close function not defined.') }
        }
    }
}
</script>

<style scoped>
/* Full screen search */
#search-overlay .close-btn {
    display: flex;
    position: relative;
}

#search-overlay .close-btn .btn {
    display: flex;
    color: var(--usu-white);
    padding: 0;
}

#search-overlay .close-btn .btn:hover,
#search-overlay .close-btn .btn:focus {
    color: var(--usu-aggie-blue);
}

#search-overlay {
    position: fixed;
    display: none;
    content: '';
    top: 0;
    left: 0;
    background: var(--usu-bright-light);
    width: 100%;
    height: 100%;
    z-index: 9999;
}

#search-overlay h2 {
    font-size: 1.5rem;
    color: var(--usu-aggie-blue);
}

#search-overlay .input-group input {
    height: 40px;
    background: transparent;
    font-size: 1.4rem;
    color: var(--usu-white);
    border: none;
    border-bottom: solid 1px var(--usu-gray);
    border-radius: 0px;
}

#search-overlay .input-group input:focus {
    background: transparent;
    outline: none;
    box-shadow: none;
    border-color: var(--usu-gray);
    color: var(--usu-white);
}

#search-overlay .input-group .btn {
    color: var(--usu-white);
    border: none;
    border-bottom: 1px solid var(--usu-gray);
    border-radius: 0px;
}

#search-overlay .input-group .btn:hover {
    color: var(--usu-aggie-blue);
}

#search-overlay .input-group .btn:focus {
    color: var(--usu-aggie-blue);
}

#search-overlay ::placeholder {
    /* Chrome, Firefox, Opera, Safari 10.1+ */
    color: var(--usu-white);
    font-weight: normal;
    background: transparent;
    opacity: 1;
    /* Firefox */
}

#search-overlay :-ms-input-placeholder {
    /* Internet Explorer 10-11 */
    color: var(--usu-white);
    font-weight: normal;
    background: transparent;
}

#search-overlay ::-ms-input-placeholder {
    /* Microsoft Edge */
    color: var(--usu-white);
    font-weight: normal;
    background: transparent;
}

#search-overlay input:-webkit-autofill,
#search-overlay input:-webkit-autofill:hover,
#search-overlay input:-webkit-autofill:focus,
#search-overlay input:-webkit-autofill:active {
    -webkit-animation: autofill 0s forwards;
    animation: autofill 0s forwards;
    color: var(--usu-white);
}

#search-overlay i {
    font-size: 1.4rem;
}

@media screen and (min-width: 992px) {
    #search-overlay h2 {
        font-size: 1.8rem;
    }

    #search-overlay .input-group input {
        height: 60px;
        font-size: 1.8rem;
    }

    #search-overlay i {
        font-size: 1.8rem;
    }
}
</style>