# Risk calculation
## An alternative way to use official data to estimate the daily fraction of infectious population (at least in Italy)
In Italy all the official data are published on a GitHub page updated by Protezione Civile (https://github.com/pcm-dpc/COVID-19), with multiple scales of geographic resolution considered. Here we focused on:

* *regional scale*: the more accurate data on the epidemiological point of view since they separately consider the **infectious**, the **recovered** and the **deaths** per day in the region;
* *provincial scale*: they only account for a variable named `total_cases` that corresponds to the sum of the **infectious**, the **recovered** and the **deaths** per day in the province.  

Actually we have reason to believe that the delta of `total_cases` between two successive days doesn’t follow the same distribution of the fraction of infected, so this variable cannot be used as proxy variable to estimate I/N.

A counter-example for the use of `total_cases` is based on a simple SIR toy model (figure below, computed in the notebook [ToyModel](../models/ToyModel.ipynb)) where in red we showed the number of infectious individuals, and in dotted light blue the `total_cases[t] - total_cases[t-1]`.
![](.\images\delta_total_cases.PNG)

To solve this problem, and to give a better estimate of the number of infected per day using italian data we combined regional and provincial data.

The formula used to compute the risk at provincial level, following the data format given by Protezione Civile, is:

$$\frac{R^i(t)}{R^{tot}(t)/R_\text{pop}} = \frac{P^i(t)}{P^{tot}(t)/P_\text{pop}}$$
where:

* $R^i(t)$: the number of *infected* at time $t$ at regional level
* $R^{tot}(t)$: the number of *total cases* at time $t$ at regional level
* $R_\text{pop}$: the *total population* of the region
* $P^i(t)$: the number of *infected* at time $t$ at province level
* $P^{tot}(t)$: the number of *total cases* at time $t$ at province level
* $P_\text{pop}$: the *total population* of the province

which translates into:

```python
P_i[t] =  R_i[t] * (R_tot[t]/R_pop) * (P_pop/P_tot[t])
```

To check if this proxy variable can improve our estimation of the fraction of infected per province we used another toy SIR model (in the notebook [ToyModel](../models/ToyModel.ipynb)) made by 4 isolated patches (provinces) with different population size and asynchronous timing of disease start. 

The figure below shows the epidemic evolution within those 4 provinces.

![](.\images\pseudo_infected.PNG)

and in this other figure we show the comparison between:

* real infected, in red;
* `total_cases[t] - total_cases[t-1]`, light blue dotted line;
* pseudo-infected, obtained through our formula.

![](.\images\comparison_with_delta_and_pseudo.PNG)

Apart from a difference in the number of infected estimated during the peak-time in two provinces, the distribution seems to fit in better than the delta of total number of cases.
