%YANG 2011
function muL_a = muL_a(day)
    global P 
    coefficients = [2.130, -3.797*10^(-1), 2.457*10^(-2), -6.778*10^(-4), 6.794*10^(-6)];
    x_values=temp(day, 0);
    muL_a = polyval(fliplr(coefficients), x_values);
    %plot(linspace(10,40,40), polyval(fliplr(coefficients),
    %(linspace(10,40,40))))  to plot temp dependent params
end
