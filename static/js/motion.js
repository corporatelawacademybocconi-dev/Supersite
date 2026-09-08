(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const header = document.querySelector('.navbar');
    const article = document.querySelector('.prose');
    const progressBar = document.querySelector('.article-reading-progress__bar');

    const updateHeader = () => {
        if (header) header.classList.toggle('is-scrolled', window.scrollY > 24);
    };

    const updateReadingProgress = () => {
        if (!article || !progressBar) return;

        const start = article.getBoundingClientRect().top + window.scrollY - 140;
        const end = start + article.offsetHeight - window.innerHeight * 0.42;
        const progress = Math.max(0, Math.min(1, (window.scrollY - start) / (end - start)));

        progressBar.style.transform = `scaleX(${progress})`;
    };

    const updateOnScroll = () => {
        updateHeader();
        updateReadingProgress();
    };

    updateOnScroll();
    window.addEventListener('scroll', updateOnScroll, { passive: true });
    window.addEventListener('resize', updateReadingProgress);

    if (reduceMotion.matches) return;

    const targets = [
        ...document.querySelectorAll(
            '.section-header, .split-layout > *, .article-grid > *, .event-list > *, .episode-list > *, .grid > *, .article-stats > *'
        )
    ];

    targets.forEach((element, index) => {
        element.classList.add('cla-reveal');
        element.style.setProperty('--reveal-delay', `${(index % 3) * 70}ms`);
    });

    if (!('IntersectionObserver' in window)) {
        targets.forEach((element) => element.classList.add('is-revealed'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
        });
    }, { rootMargin: '0px 0px -8%', threshold: 0.08 });

    targets.forEach((element) => observer.observe(element));
    const scrollZoomImages = document.querySelectorAll('.scroll-zoom');

    const updateImageZoom = () => {
        scrollZoomImages.forEach((image) => {
            const rect = image.getBoundingClientRect();
            const imageCentre = rect.top + rect.height / 2;
            const viewportCentre = window.innerHeight / 2;
            const distance = Math.abs(imageCentre - viewportCentre);
            const scale = 1 - Math.min(distance / window.innerHeight, 1) * 0.045;

            image.style.setProperty('--scroll-scale', scale.toFixed(3));
        });
    };

    updateImageZoom();
    window.addEventListener('scroll', updateImageZoom, { passive: true });
    window.addEventListener('resize', updateImageZoom);
})();