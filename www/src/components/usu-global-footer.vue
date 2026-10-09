<template>
    <section id="global-footer" class="bg-blue-darker">
        <div class="container">
            <div class="row py-3 py-lg-4">
                <div class="col-12 col-lg-3 py-3 d-flex align-items-center justify-content-center">
                    <a href="https://www.usu.edu">
                        <img class="img-fluid" src="/images/utah-state-logo.svg" width="350"
                            height="34" alt="Utah State University logo">
                    </a>
                </div>
                <div
                    class="col-12 col-lg-9 d-flex flex-row flex-lg-column justify-content-center justify-content-lg-start align-items-start">
                    <div class="left-list my-lg-1">
                        <ul>
                            <li><a href="https://www.usu.edu/map/">Maps &amp; Directions</a></li>
                            <li><a href="https://www.usu.edu/search/">Search USU</a></li>
                            <li><a href="https://www.usu.edu/safety/">Campus Safety</a></li>
                            <li><a href="https://jobs.usu.edu">Jobs</a></li>
                            <li><a href="https://www.usu.edu/contact/">Contact</a></li>
                        </ul>
                    </div>
                    <div class="right-list">
                        <ul>
                            <li><a href="https://www.usu.edu/copyright/">Disclaimers</a></li>
                            <li><a href="https://www.usu.edu/copyright/index.cfm#copyright">Copyright</a></li>
                            <li><a href="https://www.usu.edu/privacy/">Privacy</a></li>
                            <li><a href="https://www.usu.edu/accessibility/contact/">Accessibility</a></li>
                            <li><a href="https://www.usu.edu/equity/non-discrimination">Non-Discrimination</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
/* Global Footer */
#global-footer {
    margin-top: 1.5rem;
}

#global-footer li {
    padding: .2rem 0;
}

#global-footer img.img-fluid {
    width: 100%;
    margin: auto;
    max-width: 180px;
}

@media (min-width: 768px) {
    #global-footer img.img-fluid {
        max-width: 220px;
    }
}

#global-footer a {
    color: var(--usu-gray);
}

#global-footer a:hover {
    color: var(--usu-white);
}

#global-footer ul {
    padding: 0 10px;
}

#global-footer li {
    list-style-type: none;
}

#global-footer .left-list {
    text-align: right;
}

@media (min-width: 992px) {
    #global-footer ul {
        display: inline;
        padding-left: 0;
        margin: 0;
    }

    #global-footer li {
        display: inline;
        margin-right: 15px;
    }

    #global-footer .left-list {
        text-align: left;
    }

    #global-footer .right-list {
        font-size: .9rem;
    }
}
</style>