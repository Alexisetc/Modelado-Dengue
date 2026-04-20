function dydt = myODE_ELF(t,y,p)
global P

E_a = y(1);
L_a = y(2);
F_a = y(3);
E_b = y(4);
L_b = y(5);
F_b = y(6);

% Parameters to estimate
bet_ba = p(1);
bet_ab = p(2);

%aedes aegypti
Et_a = P.phi_p_a(t) * F_a - (P.mu_E_a(t) + P.psi1_a(t)) * E_a;
Lt_a = P.psi1_a(t)* E_a * (1 - ((L_a + L_b-(bet_ba*L_b))/ P.K)) - (P.mu_L_a(t) + P.psi2_a(t)) * L_a;
Ft_a = P.psi2_a(t) * P.bF_a * L_a - P.mu_F_a(t)*F_a;

%aedes albopictus
if t < 355%371 %time to start albopictus
    Et_b = 0;
    Lt_b = 0;
    Ft_b = 0;
else
    Et_b = P.phi_p_b(t) * F_b - (P.mu_E_b(t) + P.psi1_b(t)) * E_b;
    Lt_b = P.psi1_b(t) * E_b * (1 - ((L_a + L_b-(bet_ab*L_a))/ P.K)) - (P.mu_L_b(t) + P.psi2_b(t)) * L_b;
    Ft_b = P.psi2_b(t) * P.bF_b * L_b - P.mu_F_b(t)*F_b;
end

dydt = [Et_a;Lt_a;Ft_a;Et_b;Lt_b;Ft_b];

end