<template>
    <footer>
      <div class="footer-info">
        <p>© 2025 
          <a href="yku.tsukimiya.site">月宫の小站</a> 
          @
          <a href="https://github.com/bpuffer/" target="_blank">BPuffer</a>
          <!-- with 
          <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" target="_blank">GPL-3.0</a> -->
          。 保留所有权利。
        </p>
        <p>
          <a href="https://github.com/bpuffer/www.tsukimiya.site" target="_blank"><i class="fa-brands fa-github"></i>Github</a>
        </p>

        <p>
          <img src="/img/miit.png" alt="辽ICP备A1-12345678" style="height: 1.2rem;">
          <a href="https://beian.miit.gov.cn/" target="_blank">辽ICP备A1-12345678</a>
        </p>
      </div>
      <div class="sentinel"></div>
    </footer>
</template>

<style scoped>
footer {
  width: 100%;
  margin-top: 10px;
  border-top: 2px solid;
  border-image: linear-gradient(90deg, #a8a, #fdf) 1;
  background-color: #ffffffc0;
}

.footer-info {
  text-align: center;
  padding: 0;
  margin: 0;
}

.footer-info p {
  color: #333;
  margin: 0;
}

.footer-info a {
  color: inherit;
  text-decoration: underline;
}

.sentinel {
  height: 64px;
}
</style>
