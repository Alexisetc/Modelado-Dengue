%YANG 2011
function inter_lifespan = muF_a(day)
    global P 
    coefficients = [3.809*10^(-6), -3.408*10^(-4), 1.116*10^(-2), -1.590*10^(-1), 8.692*10^(-1)];
    x_values=temp(day, 0);
    inter_lifespan = polyval(coefficients, x_values);
    %plot(linspace(10,40,40), polyval((coefficients), (linspace(10,40,40))))
end
