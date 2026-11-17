# Changelog

## 0.1.1 (2026-11-17)


### ⚠ BREAKING CHANGES

* **warp:** needs a juturna version with remote protocol 1, on both sides. The default `grpc_port` is 50051 instead of 50080.
* **warp:** support sticky and stateless remote services

### Features

* **nodes:** add browser_input and browser_output nodes ([f2aa885](https://github.com/meetecho/juturna_nodes/commit/f2aa885870cc99f2a37ea6ec693ab31e2dc2c506))
* **notifier_console:** add a sink that prints messages on the terminal ([7e0486b](https://github.com/meetecho/juturna_nodes/commit/7e0486b49b566222c11ddecbb2fd146084417377))
* **notifier_console:** add a sink that prints messages on the terminal ([216e95e](https://github.com/meetecho/juturna_nodes/commit/216e95e5a030dfb555debb148e64d144d62bf818))
* **warp:** leave out the values that cannot be sent ([485ad00](https://github.com/meetecho/juturna_nodes/commit/485ad003355b70c91066e65be6a4b9112c70a239))
* **warp:** speak version 1 of the remote protocol, with a session ([40eef67](https://github.com/meetecho/juturna_nodes/commit/40eef677b7066f9c97f68bafbe87538d0bb1a01d))
* **warp:** support sticky and stateless remote services ([b8e11ce](https://github.com/meetecho/juturna_nodes/commit/b8e11ce21c2054fbb248540781d2180fd926928a))


### Bug Fixes

* **audio_file:** set payload start/end in seconds ([1254510](https://github.com/meetecho/juturna_nodes/commit/12545109200b74c1716789dff66bd8958cb8c57c))
* **audio_file:** set payload start/end in seconds ([f7d7c54](https://github.com/meetecho/juturna_nodes/commit/f7d7c546f955178551d47c12b719e42a3ed63f13))
* **audio_file:** stop passing metadata_errors to av.open, removed in pyav 19 ([d9a713a](https://github.com/meetecho/juturna_nodes/commit/d9a713a6e889b0b3c9a343ffcc21d16985a38e35))
* **audio_file:** stop passing metadata_errors to av.open, removed in pyav 19 ([127e5c0](https://github.com/meetecho/juturna_nodes/commit/127e5c02e5173eb497c9db5a96d133cc32439187))
* **audio_rtp:** count every channel in stereo chunks and their duration ([7d5d536](https://github.com/meetecho/juturna_nodes/commit/7d5d536cafea0db139d1ccb62616e39e6629495e))
* **audio_rtp:** count every channel in stereo chunks and their duration ([a5fd6cc](https://github.com/meetecho/juturna_nodes/commit/a5fd6ccb91e3005e84fa1de8627e1402c17ebe7e))
* **audio_rtp:** enlarge the socket buffer so bursts of packets are not dropped ([1303a49](https://github.com/meetecho/juturna_nodes/commit/1303a4945d4f1c9d6fc298084fde179e2d43a0b7))
* **audio_rtp:** keep the packets read while probing the stream ([5eb1a41](https://github.com/meetecho/juturna_nodes/commit/5eb1a4190535a23085754da26a88a1869c218250))
* **audio_rtp:** keep the sample format of mono audio instead of averaging into float64 ([ae0675b](https://github.com/meetecho/juturna_nodes/commit/ae0675b0c4f555af424161d4056e4b41ce9f3aab))
* **audio_rtp:** keep the sample format of mono audio instead of averaging into float64 ([77921c7](https://github.com/meetecho/juturna_nodes/commit/77921c77c7dbafc9be922994553faa58a9e682cb))
* **audio_rtp:** retry when the input cannot be opened instead of killing the worker ([e947ed2](https://github.com/meetecho/juturna_nodes/commit/e947ed2451b434cdd2ad2d3132233b1595e1988c))
* **audio_rtp:** stop losing packets, stop quickly and retry a busy port ([fdce7d4](https://github.com/meetecho/juturna_nodes/commit/fdce7d4e48e91e1291d702789771fe4d2cfe7824))
* **audio_rtp:** time out opening an idle input so stop returns quickly ([efb6d81](https://github.com/meetecho/juturna_nodes/commit/efb6d8153a398f19fb25c6df19d229d4e5937c69))
* **audio_rtp:** use logger.warning instead of the deprecated warn ([e7e5831](https://github.com/meetecho/juturna_nodes/commit/e7e5831e482b9cc2a92c7c9421e49b0066fc109f))
* **browser:** add support for v3 approach ([d53ca5d](https://github.com/meetecho/juturna_nodes/commit/d53ca5d48cb857e3978fd653709bbfe244ef0594))
* checking ultralytics format before setting params, fixed size bug for videortp ([b55dd0c](https://github.com/meetecho/juturna_nodes/commit/b55dd0c96173da1dc6aa7bc458ac48431415cbcb))
* checking ultralytics format before setting params, fixed size bug for videortp ([44df29a](https://github.com/meetecho/juturna_nodes/commit/44df29a3655d9d774fa7ec4f725bdc5beb1b8b94))
* **nodes:** stop using core symbols removed in juturna 3.0.0 ([a1f327b](https://github.com/meetecho/juturna_nodes/commit/a1f327b2ca00578f00b1fe3e56c22386a8ef34e9))
* **nodes:** stop using core symbols removed in juturna 3.0.0 ([892beca](https://github.com/meetecho/juturna_nodes/commit/892beca3101739e37a7a22a964b51e8646cc5de0))
* **warp:** report the values left out once per node ([909d0f5](https://github.com/meetecho/juturna_nodes/commit/909d0f50195a0fc27134e2822a9e1d193d721383))


### Documentation

* **audio_rtp:** drop the transcriber name and the system ffmpeg line ([aa57f84](https://github.com/meetecho/juturna_nodes/commit/aa57f84bdca50ec7e1c489f5f283f0f2f72ecc7b))
* **audio_rtp:** rewrite the README for the current node ([fd9e053](https://github.com/meetecho/juturna_nodes/commit/fd9e053138c0b8815b5f71320babb7f5b1cccc35))
* **audio_rtp:** sync the catalogue page with the readme ([09b66be](https://github.com/meetecho/juturna_nodes/commit/09b66be9eb8fa27f325653ac86564ff34f2ae82d))
* fix the node docs the code contradicts ([a19b6ce](https://github.com/meetecho/juturna_nodes/commit/a19b6cec8d6c8c9df6026cf1c31a5003e773234d))
* fix the node docs the code contradicts ([bb9d78f](https://github.com/meetecho/juturna_nodes/commit/bb9d78f0cd3ac1980ab657b09bb9d82d836b74bf))
* **nodes:** document the browser nodes ([742a6b5](https://github.com/meetecho/juturna_nodes/commit/742a6b59dec09c4c0b0e63bce667c011a05c8fba))
* stop asking for system ffmpeg for the av nodes ([49bfe60](https://github.com/meetecho/juturna_nodes/commit/49bfe60100d03f238342138d6652b243a0d84689))
* **warp:** describe the single warning for values left out ([87e4584](https://github.com/meetecho/juturna_nodes/commit/87e4584acb567f067b9d84e28dd6c8859270bfcc))

## Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
