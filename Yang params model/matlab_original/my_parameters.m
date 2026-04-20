global P
P.K = 10^5;
P.bF_a = 0.5;
P.bM_a = 0.5;
P.sigma_a = 1;
P.phi_a = @(t)phi_A(t); % 
P.psi1_a = @(t)psi1_a(t); % *
P.psi2_a = @(t)psi2_a(t);
P.mu_E_a = @(t)muE_a(t);
P.mu_L_a = @(t)muL_a(t);   
P.mu_F_a = @(t)muF_a(t)*3;  
P.phi_p_a =@(t)phi_p_a(t);
%P.bet_ab = tbd;

%Albopictus parameters
P.bF_b = 0.5;
P.bM_b = 0.5;
P.sigma_b = 1;
P.phi_b = @(t)phi_B(t);
P.psi1_b = @(t)psi1_b(t); 
P.psi2_b = @(t)psi2_b(t);
P.mu_E_b = @(t)muE_b(t);
P.mu_L_b = @(t)muL_b(t); 
P.mu_F_b = @(t)muF_b(t)*10; 
P.phi_p_b = @(t)phi_p_b(t);
%P.bet_ba = tbd;
%P.phi_p_b = 0.1;

