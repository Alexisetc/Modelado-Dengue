%temperature dependent psi_2a: 
function psi2_a_output = psi2_a(day)
    global P 
    coefficients2 = [-3.420*10^(-10), 5.153*10^(-8), -3.017*10^(-6),8.723*10^(-5), -1.341*10^(-3), 1.164*10^(-2), -5.723*10^(-2), 1.310*10^(-1)];
    x_values=temp(day, 0);
    psi2_a_output = polyval(coefficients2, x_values);
    %to plot the profile of the parameters vs temperature
    %plot((polyval(fit_dev,linspace(10,35,35)).*P.psi2_a)./(P.psi2_a-polyval(fit_dev,linspace(10,35,35))))
end
