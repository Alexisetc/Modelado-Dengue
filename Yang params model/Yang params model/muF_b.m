%Mordecai
function inter_lifespan = muF_b(day)
    global P 
    coefficients = 1000 .* [-0.000000280151205,   0.000038830897223,  -0.002030126893948,   0.049162298893216,  -0.540751134100950,   2.180587170776479];
    x_values=temp(day, 0);
    inter_lifespan = 1./polyval(coefficients, x_values);
    %plot(linspace(13, 33, 40), 1./polyval((coefficients), (linspace(13, 33, 40))))
end
