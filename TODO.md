# TODO - Search funcional con sugerencias y recientes

- [ ] Implementar backend de búsqueda:
  - [ ] endpoint JSON de sugerencias personalizadas
  - [ ] endpoint para recientes (GET/POST) en sesión
  - [ ] utilidades para normalizar/limitar recientes
- [ ] Actualizar rutas (`web_tienda/urls.py`) para nuevos endpoints
- [ ] Integrar UI de búsqueda global en `index.html` y `productos.html`
- [ ] Crear JS del buscador:
  - [ ] abrir/cerrar panel
  - [ ] autocompletado con debounce
  - [ ] render recientes + sugerencias
  - [ ] guardar búsqueda reciente al enviar
  - [ ] navegación por teclado
- [ ] Agregar estilos CSS del panel y lista de sugerencias
- [ ] Crear/actualizar pruebas en `web_tienda/tests.py` para:
  - [ ] sugerencias
  - [ ] recientes
  - [ ] flujo básico de búsqueda
- [ ] Ejecutar pruebas Django y verificar que todo pase
