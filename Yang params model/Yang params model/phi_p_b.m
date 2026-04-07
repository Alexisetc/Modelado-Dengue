function phip_b = phi_p_b(day)
    global P 
    phip_b = (phi_B(day).* P.sigma_b)./((muF_b(day))+ P.sigma_b);
    %to plot function: plot(phi_b(1:569))
    %to plot the profile of the parameters vs temperature
    %plot(polyval(fit_fecund,linspace(10,35,35)))
end