function phip_a = phi_p_a(day)
    global P 
    phip_a = (phi_A(day).* P.sigma_a)./((muF_a(day))+ P.sigma_a);
    %to plot function: plot(phi_A(1:569))
    %to plot the profile of the parameters vs temperature
    %plot(polyval(fit_fecund,linspace(10,35,35)))
end
