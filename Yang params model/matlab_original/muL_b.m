%Mordecai
function muL_b = muL_b(day)
    global P 
    psi_2b_coeffs =[0.000000003111255, -0.000000510683515, 0.000032364878841, -0.001035204429043, 0.017823943160582, -0.150962097623919, 0.491223455446361];
    eas_coeffs =  [0.000000027595905,-0.000003970863730, 0.000231119129084,-0.006946993580407, 0.109839713053612,-0.777893789484992,1.910374982086748];
    mu_L_b = @(x) (polyval(psi_2b_coeffs, x)./polyval(eas_coeffs,x))-polyval(psi_2b_coeffs,x);
    x_values=temp(day, 0);
    muL_b = mu_L_b(x_values);
    %plot(linspace(10, 40, 40), mu_L_b(linspace(10, 40, 40))) to plot temp dependent params
end
