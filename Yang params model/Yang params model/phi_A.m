function inter_fecundity = phi_A(day)
    global P 
    coefficients = [-1.515*10^(-4),1.015*10^(-2),-2.124*10^(-1),1.8,-5.4];
    x_values=temp(day, 0);
    inter_fecundity = polyval(coefficients, x_values);

    %to plot function: plot(phi_A(1:569))
    %to plot the profile of the parameters vs temperature
    %plot(polyval(fit_fecund,linspace(10,35,35)))
end
