<template>
    <div class="w-100">
        <div class="jumbotron-fluid jumbotron-full jumbotron-full-image d-flex flex-column py-3">
            <div class="flex-grow-1"></div>
            <div class="jumbotron-content xl h-bold container text-white">
                <h1 class="text-white text-shadow">
                    System Name
                </h1>
            </div>
            <div class="jumbotron-overlay"></div>
        </div>

        <div class="container">
            <div class="row">
                <div class="col-lg-8 my-5">
                    <h2>About the system</h2>

                    {{ _tmpTextAboutSystem }}
                </div>

                <div class="col-lg-4">
                    <UsuCard title="Information">
                        <div class="form-group">
                            <label for="input-name">Name</label>
                            <input type="text" class="form-control" id="input-name" placeholder="Name">
                        </div>

                        <div class="form-group">
                            <label for="input-email">Email</label>
                            <input type="email" class="form-control" id="input-email" placeholder="Email">
                        </div>

                        <div class="form-group">
                            <label for="input-message">Message</label>
                            <textarea class="form-control" id="input-message" rows="3"></textarea>
                        </div>

                        <button class="btn btn-block btn-bright-light">Request Information</button>
                    </UsuCard>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import UsuCard from '../components/usu-card.vue';
import { loremIpsum } from "lorem-ipsum";

const _tmpTextAboutSystem = loremIpsum({ count: 3, units: 'paragraphs' });
</script>

<style scoped>
.jumbotron-fluid {
    background-image: url('/images/banner-farms.png');
    background-size: cover;
    height: 300px;
    min-height: 100px;
}

.col-lg-4 {
    position: relative;
    top: -100px;
    margin-bottom: -100px;
    z-index: 50;
}
</style>
