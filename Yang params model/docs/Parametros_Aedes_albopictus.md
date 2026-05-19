# Parámetros dependientes de temperatura para *Aedes albopictus*

Documento equivalente a `Parametros Aedes Aegypty.pdf` (modelo Yang), adaptado para
*Aedes albopictus* (Skuse, 1894), el "mosquito tigre asiático". Mantiene la misma
estructura, notación y fórmulas del documento original; los parámetros llevan el
subíndice **`b`** (de *albopictus*) para diferenciarlos de los de *aegypti* (subíndice
`a` en el documento original).

Fuentes principales:

* **Delatte, H., Gimonneau, G., Triboire, A., & Fontenille, D. (2009).** *Influence of
  temperature on immature development, survival, longevity, fecundity, and gonotrophic
  cycles of Aedes albopictus, vector of Chikungunya and Dengue in the Indian Ocean.*
  Journal of Medical Entomology, 46(1), 33–41. → estadio de huevo.
* **Mordecai, E. A., Cohen, J. M., Evans, M. V., Gudapati, P., Johnson, L. R., Lippi,
  C. A., et al. (2017).** *Detecting the impact of temperature on transmission of Zika,
  dengue, and chikungunya using mechanistic models.* PLoS Neglected Tropical Diseases,
  11(4), e0005568. → respuestas térmicas (Brière / cuadrática) para tasas
  acuáticas y de adultos (**Tabla S1**).
* **Marini, G., Manica, M., Delucchi, L., Pugliese, A., & Rosà, R. (2020).**
  *Spatio-temporal distribution of Aedes albopictus in Europe and its prospective range
  expansion under climate change.* Veterinary Italiana, 56(2), 109–118. → complemento
  para climas templados.

## Diferencias biológicas relevantes frente a *Ae. aegypti*

| Rasgo | *Ae. aegypti* | *Ae. albopictus* | Implicación para los parámetros |
|---|---|---|---|
| Distribución térmica | Tropical estricta | Tropical y templada | albopictus tolera temperaturas más bajas |
| Diapausa de huevos | Limitada | Presente en cepas templadas | huevos resisten frío prolongado |
| Hábitat de crías | Antrópico (interior) | Peri-doméstico (exterior) | mayor exposición a fluctuaciones térmicas |
| Temperatura óptima de mordedura | ≈ 29 °C | ≈ 26–28 °C | desplazamiento térmico en `a_b(T)` |
| Tmin biológico | ≈ 13–15 °C | ≈ 8–11 °C | actividad en estaciones frescas |
| Tmax biológico | ≈ 35–40 °C | ≈ 35–40 °C | similar a aegypti |
| Hospedador preferente | Antropofílico estricto | Generalista (mamífero/ave) | menor competencia vectorial en algunos contextos |

Estas diferencias se reflejan numéricamente en los coeficientes `q`, `Tmin`, `Tmax`
de las funciones de respuesta térmica de Mordecai *et al.* (2017), reportados en
la **Tabla S1** de su material suplementario.

---

## 1. Funciones de respuesta térmica

Como en el documento de *aegypti*, las tasas demográficas dependen de la temperatura
mediante dos formas funcionales canónicas:

**Brière (asimétrica)**

$$f_B(T;q,T_{\min},T_{\max}) = q\,T\,(T-T_{\min})\,\sqrt{T_{\max}-T}\qquad \text{para } T_{\min} \le T \le T_{\max}$$

**Cuadrática (simétrica)**

$$f_Q(T;q,T_{\min},T_{\max}) = -q\,(T-T_{\min})\,(T-T_{\max})\qquad \text{para } T_{\min} \le T \le T_{\max}$$

Ambas se anulan fuera del intervalo `[Tmin, Tmax]`.

---

## 1.1 Estadio de huevo (E_b)

La probabilidad de eclosión `p_b(T)` y el tiempo medio de embriogénesis `τ_b(T)` se
estiman a partir de los experimentos de **Delatte *et al.* (2009)** con la cepa
*Ae. albopictus* de La Réunion bajo ocho regímenes térmicos constantes:

**Tabla 1. Eclosión y embriogénesis de *Ae. albopictus* (Delatte *et al.* 2009).**

| T (°C) | n huevos | p_b (%) | τ_b (días, media ± DE) |
|---:|---:|---:|---:|
| 5  | 180 |  4.4 | 11.0 ± 1.3 |
| 10 | 100 |  4.0 |  2.0 ± 0.0 |
| 15 | 110 |  8.2 |  7.4 ± 1.8 |
| 20 | 130 | 66.9 |  2.9 ± 0.4 |
| 25 | 130 | 49.2 |  4.5 ± 0.7 |
| 30 | 140 | 51.4 |  6.7 ± 0.7 |
| 35 | 190 | 10.0 |  7.1 ± 0.8 |
| 40 | 100 |  0.0 | — |

**Tasas derivadas (siguiendo la convención del documento original):**

$$\psi_{1b}(T) \;=\; \frac{p_b(T)}{\tau_b(T)} \qquad \text{(tasa de eclosión efectiva)}$$

$$\mu_{Eb}(T) \;=\; \frac{1-p_b(T)}{\tau_b(T)} \qquad \text{(mortalidad de huevos)}$$

* `ψ_{1b}(T)`: huevos viables que eclosionan por unidad de tiempo. Máximo
  empírico en torno a 20 °C (≈ 0.23 día⁻¹) por el corto `τ_b` (2.9 días) y
  la alta `p_b` (66.9 %).
* `μ_{Eb}(T)`: mortalidad embrionaria. Máxima a 10 °C
  (≈ 0.48 día⁻¹) y a 40 °C (no hay eclosiones; `μ_{Eb}` queda
  indeterminado y se considera total).

**Nota sobre 10 °C.** El valor reportado de `τ_b = 2 ± 0` días en Delatte *et al.*
(2009) contradice la tendencia esperada (mayor `τ_b` a menor T). Se mantiene la
tabla tal como fue publicada; en el ajuste continuo se trata como punto
influyente menor. La fila de 40 °C se incluye para acotar el dominio térmico
superior: con cero eclosiones, `μ_{Eb}(40) = 1/τ_b → 1` día⁻¹ por convención.

---

## 1.2 Estadio acuático (L_b): larvas y pupas

Sigue la formulación del documento original de *aegypti*, con `MDR_b(T)` (tasa de
desarrollo del mosquito, *Mosquito Development Rate*) y `p_{EAb}(T)` (probabilidad
de supervivencia huevo→adulto) tomadas de **Mordecai *et al.* (2017)**, Tabla S1.

$$\psi_{2b}(T) \;=\; \mathrm{MDR}_b(T) \;=\; f_B(T;\, 6.33\!\times\!10^{-5},\, 8.7,\, 39.6)$$

$$p_{EAb}(T) \;=\; f_Q(T;\, 3.56\!\times\!10^{-3},\, 9.1,\, 39.3)$$

$$\mu_{Lb}(T) \;=\; \psi_{2b}(T)\,\left(\frac{1}{p_{EAb}(T)} - 1\right)$$

**Tabla 2. Parámetros térmicos del estadio acuático de *Ae. albopictus* (Mordecai 2017, Tabla S1).**

| Parámetro | Forma | q | Tmin (°C) | Tmax (°C) | Topt (°C) | Unidades |
|---|---|---:|---:|---:|---:|---|
| MDR_b | Brière | 6.33 × 10⁻⁵ | 8.7 | 39.6 | 32.6 | día⁻¹ |
| p_{EAb} | Cuadrática | 3.56 × 10⁻³ | 9.1 | 39.3 | 24.2 | adimensional |

**Interpretación.**

* `MDR_b(T)` alcanza su máximo en `Topt ≈ 32.6 °C` (≈ 0.082 día⁻¹), reflejando
  desarrollo larvario más rápido en clima cálido.
* `p_{EAb}(T)` es máxima en `Topt ≈ 24.2 °C` (≈ 0.79). El óptimo de supervivencia
  acuática es más bajo que el óptimo de velocidad de desarrollo: a 32 °C las larvas
  se desarrollan rápido pero mueren más.
* `μ_{Lb}(T)` combina ambas: tiene un mínimo cerca de 24–26 °C y crece a los
  extremos.

---

## 1.3 Estadio adulto (F_b)

Tres tasas, todas de Mordecai *et al.* (2017), Tabla S1:

* **Tasa de mordedura** `a_b(T)`: contactos vector–hospedador por hembra por día.
* **Fecundidad** `EFOC_b(T)`: huevos por hembra por ciclo gonotrófico (*Eggs per Female per Oviposition Cycle*).
* **Longevidad** `lf_b(T)`: vida media de la hembra adulta.

$$a_b(T) \;=\; f_B(T;\, 1.90\!\times\!10^{-4},\, 10.4,\, 38.1)$$

$$\mathrm{EFOC}_b(T) \;=\; f_B(T;\, 4.77\!\times\!10^{-2},\, 7.9,\, 35.6)$$

$$lf_b(T) \;=\; f_Q(T;\, 1.39,\, 13.5,\, 31.4) \qquad \text{[días]}$$

$$\phi_b(T) \;=\; \mathrm{EFOC}_b(T)\cdot a_b(T) \qquad \text{(tasa de oviposición)}$$

$$\mu_{Fb}(T) \;=\; \frac{1}{lf_b(T)}$$

$$\phi_{1b}(T) \;=\; \frac{\sigma\,\phi_b(T)}{\mu_{Fb}(T) + \sigma},\qquad \sigma=1$$

donde `φ_{1b}` es el reclutamiento efectivo de huevos por adulto (descuento por
mortalidad durante el ciclo, con maduración `σ = 1` día⁻¹ como en el documento
original).

**Tabla 3. Parámetros térmicos del adulto *Ae. albopictus* (Mordecai 2017, Tabla S1).**

| Parámetro | Forma | q | Tmin (°C) | Tmax (°C) | Topt (°C) | Unidades |
|---|---|---:|---:|---:|---:|---|
| a_b | Brière | 1.90 × 10⁻⁴ | 10.4 | 38.1 | 31.8 | día⁻¹ |
| EFOC_b | Brière | 4.77 × 10⁻² | 7.9  | 35.6 | 29.4 | huevos·hembra⁻¹·ciclo⁻¹ |
| lf_b | Cuadrática | 1.39 | 13.5 | 31.4 | 22.5 | día |

**Interpretación.**

* `a_b(T)` máxima en ≈ 31.8 °C (≈ 0.42 día⁻¹). Los óptimos de mordedura de
  *albopictus* son menores que los de *aegypti* (≈ 35 °C), consistente con su
  distribución templada.
* `EFOC_b(T)` máxima en ≈ 29.4 °C, también desplazada hacia clima más fresco que
  la EFD de *aegypti*.
* `lf_b(T)` es máxima cerca de 22.5 °C (≈ 28 días), evidencia clara de mayor
  longevidad en regímenes templados.

---

## 1.4 Resumen y comparación con *Ae. aegypti*

**Tabla 4. Comparación de parámetros térmicos: *Ae. aegypti* vs. *Ae. albopictus*
(Mordecai *et al.* 2017, Tabla S1).**

| Parámetro | Especie | Forma | q | Tmin (°C) | Tmax (°C) |
|---|---|---|---:|---:|---:|
| **Tasa de mordedura `a`** | aegypti | Brière | 2.02 × 10⁻⁴ | 13.8 | 40.0 |
|                            | albopictus | Brière | 1.90 × 10⁻⁴ | 10.4 | 38.1 |
| **Fecundidad** (`EFD` aeg. / `EFOC` alb.) | aegypti | Brière | 8.16 × 10⁻³ | 14.7 | 34.4 |
|                                              | albopictus | Brière | 4.77 × 10⁻² | 7.9 | 35.6 |
| **MDR**                    | aegypti | Brière | 7.83 × 10⁻⁵ | 11.6 | 39.1 |
|                            | albopictus | Brière | 6.33 × 10⁻⁵ | 8.7 | 39.6 |
| **p_{EA}**                 | aegypti | Cuadrática | 5.99 × 10⁻³ | 13.6 | 38.3 |
|                            | albopictus | Cuadrática | 3.56 × 10⁻³ | 9.1 | 39.3 |
| **Longevidad `lf`**        | aegypti (DENV) | Cuadrática | 0.144 | 9.0 | 37.7 |
|                            | albopictus | Cuadrática | 1.39 | 13.5 | 31.4 |

**Observaciones clave.**

1. **Tmin sistemáticamente más bajo en `albopictus`** salvo en `lf` (donde aegypti
   sobrevive a temperaturas más bajas según el dato de Mordecai 2017, pero con
   `q` mucho menor y curva más plana). Esto explica la expansión del mosquito tigre
   a zonas templadas (sur de Europa, EE.UU., Andes).
2. **Tmax similar o ligeramente menor** en `albopictus` para `a`, `EFOC` y `lf`:
   no es más tolerante al calor extremo.
3. **`q` mayor para EFOC en albopictus (4.77e-2 vs 8.16e-3)**: la magnitud absoluta
   de las funciones se distribuye distinto; comparar curvas, no sólo `q`. Ver
   figuras.
4. **`lf` en albopictus es cualitativamente distinta**: Tmin = 13.5 y Tmax = 31.4
   acotan una ventana térmica estrecha, con Topt ≈ 22.5 °C y vida media máxima
   ≈ 28 días.

---

## 1.5 Figuras

* `figures/albopictus_egg_stage.png` — `p_b(T)`, `τ_b(T)`, `ψ_{1b}(T)` y
  `μ_{Eb}(T)` a partir de la Tabla 1 de Delatte *et al.* (2009).
* `figures/albopictus_params_overview.png` — panel de 2 × 3 con las funciones
  continuas: `a_b`, `EFOC_b`, `MDR_b`, `p_{EAb}`, `lf_b` y `φ_{1b}` para *albopictus*
  (línea continua) superpuestas con las equivalentes de *aegypti* (línea discontinua)
  donde aplica, en el rango 5–45 °C.

Ambas figuras se generan con `plot_albopictus_params.py` en este mismo directorio:

```bash
cd "Yang params model/docs"
python plot_albopictus_params.py
```

Requiere `numpy`, `matplotlib` y `pandas`.

---

## 1.6 Referencias

1. Delatte, H., Gimonneau, G., Triboire, A., & Fontenille, D. (2009). Influence
   of temperature on immature development, survival, longevity, fecundity, and
   gonotrophic cycles of *Aedes albopictus*, vector of Chikungunya and Dengue in
   the Indian Ocean. *Journal of Medical Entomology*, 46(1), 33–41.
   <https://doi.org/10.1603/033.046.0105>
2. Mordecai, E. A., Cohen, J. M., Evans, M. V., Gudapati, P., Johnson, L. R.,
   Lippi, C. A., Miazgowicz, K., Murdock, C. C., Rohr, J. R., Ryan, S. J.,
   Savage, V., Shocket, M. S., Stewart Ibarra, A., Thomas, M. B., & Weikel, D. P.
   (2017). Detecting the impact of temperature on transmission of Zika, dengue,
   and chikungunya using mechanistic models. *PLoS Neglected Tropical Diseases*,
   11(4), e0005568. <https://doi.org/10.1371/journal.pntd.0005568>
   (parámetros tomados de la **Tabla S1** del material suplementario).
3. Marini, G., Manica, M., Delucchi, L., Pugliese, A., & Rosà, R. (2020).
   Spatio-temporal distribution of *Aedes albopictus* in Europe and its
   prospective range expansion under climate change. *Veterinary Italiana*,
   56(2), 109–118. <https://doi.org/10.12834/VetIt.1903.10336.3>
4. Yang, H. M., Macoris, M. L. G., Galvani, K. C., Andrighetti, M. T. M., &
   Wanderley, D. M. V. (2009). Assessing the effects of temperature on the
   population of *Aedes aegypti*, the vector of dengue. *Epidemiology and
   Infection*, 137(8), 1188–1202. (referencia del documento original de aegypti).

