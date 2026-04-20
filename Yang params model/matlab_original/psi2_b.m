%temperature dependent psi_2b from Mordecai: 
function psi2_b_output = psi2_b(day)
    global P 
    coefficients2 = [0.000000003111255, -0.000000510683515, 0.000032364878841, -0.001035204429043, 0.017823943160582, -0.150962097623919, 0.491223455446361];
    x_values=temp(day, 0);
    psi2_b_output = polyval(coefficients2, x_values);
    %to plot the profile of the parameters vs temperature
    %plot(linspace(10, 40, 40), polyval((coefficients2), (linspace(10, 40, 40))))
end
