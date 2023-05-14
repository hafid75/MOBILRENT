import smartpy as sp


# Définition du smart contract
class RentalCarToken(sp.contract):
    def __init__(self, initialSupplyPerFleet):
        self.init(
            totalSupply=0,
            balances={},
            investors={},
            carFleet={},
            nextCarId=0,
            initialSupplyPerFleet=initialSupplyPerFleet
        )

    @sp.entry_point
    def buyTokens(self, params):
        # Calcul du nombre de tokens à acheter en fonction du montant envoyé
        tokenAmount = params.amount * 10  # 1 token = 10€
        sp.verify(tokenAmount > 0, "Amount must be positive")

        # Vérification que l'investisseur a suffisamment de fonds
        sp.verify(self.data.balances[sp.sender] >= tokenAmount, "Insufficient balance")

        # Ajout des tokens au compte de l'investisseur
        self.data.balances[sp.sender] -= tokenAmount
        if sp.sender in self.data.investors:
            self.data.investors[sp.sender] += tokenAmount
        else:
            self.data.investors[sp.sender] = tokenAmount

    @sp.entry_point
    def sellTokens(self, params):
        # Vérification que l'investisseur possède suffisamment de tokens
        sp.verify(self.data.investors[sp.sender] >= params.amount, "Insufficient balance")

        # Retrait des tokens du compte de l'investisseur
        self.data.investors[sp.sender] -= params.amount
        self.data.balances[sp.sender] += params.amount

    @sp.entry_point
    def addCar(self, params):
        # Vérification que l'appelant est le propriétaire du contrat
        sp.verify(sp.sender == self.owner, "Only the owner can add a car")

        # Ajout d'un véhicule à la flotte
        carId = self.data.nextCarId
        self.data.carFleet[carId] = {
            "model": params.model,
            "rentalPrice": params.rentalPrice,
            "owner": self.owner,
            "isRented": False
        }
        self.data.nextCarId += 1

        # Calcul du nombre de tokens associé à la flotte
        if self.data.nextCarId % 10 == 0:
            fleetId = self.data.nextCarId // 10 - 1
            fleetTokenAmount = self.data.initialSupplyPerFleet
            self.data.totalSupply += fleetTokenAmount
            self.data.balances[self.owner] += fleetTokenAmount
            self.data.carFleet[fleetId] = {
                "tokenAmount": fleetTokenAmount
            }

    @sp.entry_point
    def rentCar(self, params):
        # Vérification que le véhicule est disponible
        sp.verify(self.data.carFleet[params.carId]["isRented"] == False, "Car is already rented")

        # Débit du montant de la location en tokens
        tokenAmount = self.data.carFleet[params.carId // 10]["tokenAmount"] * self.data.carFleet[params.carId][
            "rentalPrice"]
        sp.verify(self.data.investors[sp.sender] >= tokenAmount, "Insufficient balance")
        self.data.investors[sp.sender] -= tokenAmount

        # Mise à jour de l'état du véhicule
        self.data.carFleet[params.carId]["isRented"] = True
        self.data.carFleet[params.carId]["renter"] = sp.sender

        # Versement des fonds au propriétaire du contrat
        self.data.investors[self.data.carFleet[params.carId]["owner"]] += tokenAmount

    @sp.entry_point
    def returnCar(self, params):
        # Vérification que l'appelant est le locataire du véhicule
        sp.verify(self.data.carFleet[params.carId]["renter"] == sp.sender, "Only the renter can return the car")

        # Mise à jour de l'état du véhicule
        self.data.carFleet[params.carId]["isRented"] = False
        self.data.carFleet[params.carId]["renter"] = None

    @sp.entry_point
    def withdrawDividends(self, params):
        # Vérification que l'investisseur a des dividendes à récupérer
        sp.verify(self.data.investors[sp.sender] > 0, "No dividends to withdraw")

        # Retrait des dividendes du compte de l'investisseur
        dividends = self.data.investors[sp.sender]
        self.data.investors[sp.sender] = 0
        sp.transfer(sp.sender, dividends)


# Initialisation du contrat avec 10 000 tokens par flotte
contract = sp.deploy(RentalCarToken(10000))

