# Livello 6: Cloud

La stessa rete che sai già fare, nel datacenter di qualcun altro. Tutto sul piano gratuito: AWS Free Tier o Azure, e Cloudflare.

---

## 17. Certificazione cloud base

AWS Cloud Practitioner o Microsoft AZ-900: una delle due. Studio pubblico come per il CCNA: pagina `site/cloud/` con avanzamento. Esame vero, prenotato con una data. Costo circa 100 euro: chiedi a Stefano se lo copre lui come investimento.

**Fatta quando:** passato. Badge sul CV e su LinkedIn.

**Riga CV:** AWS Cloud Practitioner or AZ-900, passed

## 18. VPC a mano

Dalla console: una VPC con subnet pubblica e privata, route table, internet gateway, NAT gateway (attenzione ai costi: spegnilo a fine lab), security group e NACL. Una VM in ciascuna subnet. Dimostra cosa raggiunge cosa. Poi distruggi tutto.

**Fatta quando:** la nota di lab mappa ogni concetto AWS al concetto di rete che già conosci (subnet, VLAN, ACL, NAT) e dice dove le due cose non coincidono.

**Riga CV:** Cloud networking: VPC, subnets, route tables, security groups

## 19. Terraform

Rifai la missione 18 in Terraform: `terraform plan`, `apply`, `destroy`. State nel bucket. Poi un cambiamento (aggiungi una subnet) e guarda il plan prima di applicare. Repo pubblico `lab-terraform`.

**Fatta quando:** `apply` e `destroy` girano puliti tre volte di fila, e il README spiega cosa fa lo state e perché non va in git.

**Riga CV:** Infrastructure as code with Terraform, state, plan and apply

## 20. Cloudflare Tunnel e Access

Un servizio del lab di casa (NetBox o LibreNMS) pubblicato su `lab.albertstein.link` senza aprire porte sul router di casa: Cloudflare Tunnel. Davanti, Cloudflare Access: entra solo chi ha la tua email o quella di Stefano, con codice via mail.

**Fatta quando:** da fuori casa il servizio si apre solo dopo il login Access, e la nota di lab spiega cosa vede e cosa non vede un attaccante rispetto a una porta aperta.

**Riga CV:** Zero Trust access to a home-lab service via Cloudflare Tunnel
